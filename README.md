**Project Overview**
- **Name:**     healthcare_msgs_demonstration
- 
- **Purpose:** Demonstrates publishing EEG data (using `healthcare_msgs/msg/biosensing/raw_biosignals/EEG.msg`) from a Neurosity, openBCI device or a simulator and storing it in JSONL format for downstream processing.

**Supported OS**: Linux (instructions are written and tested for a Linux desktop/server environment).

**High-level components**
- `ros2_hc_drv`: ROS2 Python node that publishes `Healthcare_msg` data.
- `eeg_saver.py`: Subscriber node that saves `healthcare_msgs/EEG` messages to `~/neurosity_logs/eeg_data.jsonl` (JSONL: one JSON object per line).
- `eeg_simulator.py`: Optional simulator that publishes synthetic EEG data in the same `healthcare_msgs` format for testing without hardware.
- `start.sh`: Orchestration script that prepares the environment, builds packages (if needed), and starts the driver/simulator + saver.
- `test_eeg_integration.py`: Automated integration test that validates the entire EEG pipeline (data format, channel count, sample consistency, quality scores).
- `visualize_eeg.py`: Visualization and analysis tool that generates time-domain and frequency-spectrum plots from stored EEG data.

**Quick start (tested workflow)**
1. Open a terminal on Linux.
2. Clone this repo into your ROS2 workspace `src/` (if not present):

```bash
# from your workspace root (example: ~/ros2_ws)
cd ~/ros2_ws/src
# git clone <this-repo>  (if not already present)
```

3. Run the setup/start script (creates/uses venv, sources ROS2, builds if required):

```bash
cd ~/ros2_ws/src/-healthcare_msgs_demonstration
# Run with real device (requires .env credentials and device online)
./start.sh

# Or run in SIMULATOR mode (no device needed):
SIMULATE=1 ./start.sh
```

4.  View stored EEG samples (JSONL)
head -3 ~/neurosity_logs/eeg_data.jsonl | python3 -m json.tool
```

**Environment details and assumptions**
- Python venv default path: `~/neurosity-venv` (configurable via `VENV_PATH` env var)
- ROS2 distro default: `jazzy` (configurable via `ROS_DISTRO` env var)
- Workspace default: `~/ros2_ws` (configurable via `WORKSPACE` env var)
- Credential file for Neurosity (when using Neurosity device): place `.env` in the `neurosity_driver` package directory, example keys:

```
NEUROSITY_DEVICE_ID=your_device_id
NEUROSITY_EMAIL=you@example.com
NEUROSITY_PASSWORD=supersecret
```
