"""System metrics collection module."""
import os
import time
import psutil
import socket
import subprocess
import json
from typing import Dict, Any, List
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from .logs import LogMonitor

@dataclass
class ServiceStatus:
    name: str
    status: str
    response_time: float
    error: str = None

class MetricsCollector:
    def __init__(self):
        self._last_cpu_times = psutil.cpu_times()
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._log_monitor = LogMonitor()
    
    def _get_cpu_metrics(self) -> Dict[str, float]:
        """Get detailed CPU metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_freq = psutil.cpu_freq()
            return {
                'usage': cpu_percent,
                'frequency': cpu_freq.current if cpu_freq else 0,
                'cores': psutil.cpu_count()
            }
        except Exception as e:
            return {'usage': 0, 'frequency': 0, 'cores': 0, 'error': str(e)}
    
    def _get_memory_metrics(self) -> Dict[str, Any]:
        """Get detailed memory metrics."""
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            return {
                'total': mem.total,
                'available': mem.available,
                'percent': mem.percent,
                'swap_total': swap.total,
                'swap_used': swap.used,
                'swap_percent': swap.percent
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_disk_metrics(self) -> Dict[str, Any]:
        """Get disk usage metrics."""
        try:
            disk = psutil.disk_usage('/')
            io = psutil.disk_io_counters()
            return {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent,
                'read_bytes': io.read_bytes if io else 0,
                'write_bytes': io.write_bytes if io else 0
            }
        except Exception as e:
            return {'error': str(e)}

    def _get_mount_points(self) -> List[Dict[str, Any]]:
        """Get all mount points and their status."""
        mount_points = []
        try:
            partitions = psutil.disk_partitions(all=False)
            
            for partition in partitions:
                if partition.fstype in ('squashfs', 'tmpfs', 'devtmpfs', 'devpts', 'proc', 'sysfs', 'securityfs'):
                    continue
                    
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    mount_info = {
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'opts': partition.opts,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent,
                        'status': 'mounted'
                    }
                    
                    if partition.device.startswith('/dev/'):
                        mount_points.append(mount_info)
                        
                except PermissionError:
                    mount_points.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'opts': partition.opts,
                        'status': 'error',
                        'error': 'Permission denied'
                    })
                except Exception as e:
                    if partition.device.startswith('/dev/'):
                        mount_points.append({
                            'device': partition.device,
                            'mountpoint': partition.mountpoint,
                            'fstype': partition.fstype,
                            'opts': partition.opts,
                            'status': 'error',
                            'error': str(e)
                        })
                        
        except Exception as e:
            mount_points.append({
                'device': 'Unknown',
                'mountpoint': 'Unknown',
                'fstype': 'Unknown',
                'status': 'error',
                'error': f"Failed to get mount points: {str(e)}"
            })
            
        return mount_points if mount_points else [{
            'device': 'No devices found',
            'mountpoint': '-',
            'fstype': '-',
            'status': 'error',
            'error': 'No mount points available'
        }]

    def _get_system_services(self) -> List[Dict[str, Any]]:
        """Get all system services with issues."""
        try:
            cmd = [
                "systemctl",
                "--no-pager",
                "--no-legend",
                "list-units",
                "--type=service",
                "--all"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            services = []
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 4:
                    service_name = parts[0]
                    load_status = parts[1]
                    active_status = parts[2]
                    sub_status = parts[3]
                    
                    if any(status in (load_status, active_status, sub_status) 
                          for status in ['failed', 'error', 'inactive', 'exited', 'dead', 'unknown']):
                        services.append({
                            'name': service_name,
                            'status': active_status,
                            'sub_status': sub_status,
                            'load_status': load_status,
                            'response_time': 0
                        })
            
            return services
            
        except subprocess.CalledProcessError as e:
            return [{
                'name': 'systemctl',
                'status': 'error',
                'error': f'Failed to get services: {str(e)}',
                'response_time': 0
            }]
        except Exception as e:
            return [{
                'name': 'unknown',
                'status': 'error',
                'error': f'Error reading services: {str(e)}',
                'response_time': 0
            }]

    def _get_partition_info(self, partition_num: int) -> Dict[str, Any]:
        """Get partition information from system command."""
        try:
            result = subprocess.run(
                f"source ~/.bashrc && getsysinfo_partition{partition_num}",
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    return data.get("partition1", {})
                except json.JSONDecodeError:
                    return {"error": "Invalid JSON data received"}
            return {"error": "No data received"}
            
        except subprocess.CalledProcessError as e:
            return {"error": f"Command failed: {str(e)}"}
        except Exception as e:
            return {"error": f"Error getting partition info: {str(e)}"}

    def _get_all_partitions_info(self) -> Dict[str, Any]:
        """Get information from all partitions."""
        return {
            f"partition{i}": self._get_partition_info(i)
            for i in range(1, 4)
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Collect all system metrics and logs."""
        metrics = {
            'timestamp': time.time(),
            'cpu': self._get_cpu_metrics(),
            'memory': self._get_memory_metrics(),
            'disk': self._get_disk_metrics(),
            'mount_points': self._get_mount_points(),
            'services': self._get_system_services(),
            'logs': self._log_monitor.get_system_logs(),
            'partitions': self._get_all_partitions_info()
        }
        
        return metrics
    
    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)