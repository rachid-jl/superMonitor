"""Log monitoring module using journalctl."""
import subprocess
from datetime import datetime
from typing import List, Dict

class LogMonitor:
    def get_system_logs(self, limit: int = 10) -> List[Dict]:
        """Get system logs from journalctl focusing on errors and failures."""
        try:
            # Get logs since last boot, priority error and above, in JSON format
            cmd = [
                "journalctl",
                "-b",  # since last boot
                "-p", "err",  # priority error and above
                "-n", str(limit),  # limit number of entries
                "--no-pager",
                "--output=short"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            logs = []
            for line in result.stdout.splitlines():
                try:
                    if line.strip():
                        # Parse the standard journalctl output format
                        parts = line.split(" ", 3)
                        if len(parts) >= 4:
                            timestamp_str = " ".join(parts[0:2])
                            try:
                                timestamp = datetime.strptime(timestamp_str, "%b %d %H:%M:%S")
                                # Add current year
                                timestamp = timestamp.replace(year=datetime.now().year)
                            except ValueError:
                                timestamp = datetime.now()
                            
                            logs.append({
                                'timestamp': timestamp,
                                'level': 'ERROR',
                                'message': parts[3].strip()
                            })
                except Exception:
                    continue
            
            return logs
            
        except subprocess.CalledProcessError:
            return [{
                'timestamp': datetime.now(),
                'level': 'ERROR',
                'message': 'Failed to retrieve system logs'
            }]
        except Exception as e:
            return [{
                'timestamp': datetime.now(),
                'level': 'ERROR',
                'message': f'Error reading logs: {str(e)}'
            }]