# Node.js System Monitor

A real-time system monitoring tool built with Node.js and Python, providing comprehensive insights into your system's performance and health.

## 🚀 Features

- **Real-time Monitoring**
  - CPU usage and frequency
  - Memory utilization
  - Disk I/O statistics
  - System services status
  - Mount points information
  - System logs

- **Rich Terminal UI**
  - Interactive dashboard
  - Color-coded metrics
  - Auto-refreshing displays
  - Easy-to-read layouts

- **Cross-platform Support**
  - Linux
  - macOS
  - Windows

## 📋 Requirements

- Node.js 14+
- Python 3.7+
- npm or yarn

## 🛠️ Installation

### Using npm

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies
python3 -m pip install -r requirements.txt
```

### Using yarn

```bash
# Install Node.js dependencies
yarn install

# Install Python dependencies
python3 -m pip install -r requirements.txt
```

### Offline Installation

```bash
# Make the installation script executable
chmod +x install.sh

# Run the installation script
./install.sh
```

## 🚀 Usage

### Start the Monitor

```bash
# Using npm
npm run monitor

# Using Python directly
python3 system_monitor.py
```

### Configuration

Edit `monitor/config.py` to customize:
- Refresh rate
- Warning thresholds
- Monitored services
- Log limits

```python
# Example configuration
REFRESH_RATE = 2  # seconds
LOG_LIMIT = 10

THRESHOLDS = {
    'cpu': {
        'warning': 70,
        'critical': 90
    },
    'memory': {
        'warning': 70,
        'critical': 90
    }
}
```

## 📊 Metrics Explained

### CPU Metrics
- Usage percentage
- Current frequency
- Core count

### Memory Metrics
- Total available memory
- Used memory
- Swap usage

### Disk Metrics
- Disk usage percentage
- Read/Write operations
- I/O throughput

### Service Monitoring
- Service status
- Response time
- Error reporting

## 🔧 Troubleshooting

### Common Issues

1. **Permission Denied**
   ```bash
   sudo chmod +x system_monitor.py
   ```

2. **Missing Dependencies**
   ```bash
   python3 -m pip install --upgrade -r requirements.txt
   ```

3. **Python Version Error**
   - Ensure Python 3.7+ is installed
   ```bash
   python3 --version
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

MIT License - feel free to use this project for any purpose.

## 📬 Support

- Create an issue for bug reports
- Submit feature requests through issues
- Check existing issues before creating new ones

## 🔄 Updates

Check the repository regularly for updates and improvements. Pull the latest changes:

```bash
git pull origin main
npm install
python3 -m pip install -r requirements.txt
```# superMonitor
