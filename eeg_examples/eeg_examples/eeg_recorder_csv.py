#!/usr/bin/env python3
"""
EEG Data Saver Node

Subscribes to the /neurosity/eeg topic and saves all incoming messages
to a csv file in the healthcare_msgs format.

Each line contains a fully serialized EEG message with all fields including:
- header (timestamp, frame_id)
- session_id
- sample_size
- eeg (flattened array of samples)
- quality (per-channel quality scores)
"""

import os
import csv
from pathlib import Path
import rclpy
from rclpy.node import Node
from healthcare_msgs.msg import EEG, EEGInfo, DeviceInfo

class EEGRecorderCSV(Node):
    def __init__(self):
        super().__init__('eeg_csv_logger')
        
        self.log_dir = Path(os.path.expanduser('~/neurosity_logs'))
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.eeg_file = self.log_dir / 'eeg_data.csv'
        self.metadata_file = self.log_dir / 'eeg_metadata.csv'
        
        self.channel_size = None  # Will be set from DeviceInfo
        self.metadata_written = False
        
        # Subscriptions
        self.create_subscription(EEGInfo, '/neurosity/eeg_info', self.eeg_info_callback, 10)
        self.create_subscription(EEG, '/neurosity/eeg', self.eeg_callback, 10)
        
        self.message_count = 0
        self.get_logger().info(f'EEG CSV Logger initialized. Data will be saved to: {self.eeg_file}')

    def eeg_info_callback(self, msg: EEGInfo):
        """Handle DeviceInfo and write metadata CSV"""
        self.channel_size = msg.channel_size
        
        if not self.metadata_written:
            metadata = {
                'channel_size': msg.channel_size,
                'units': msg.units,
                'montage_type': msg.montage_type,
                'selected_preprocessing': msg.selected_preprocessing,
                'electrode_sites': msg.electrode_sites,
                'electrode_physical_type': msg.electrode_physical_type,
                'signal_mode': msg.signal_mode,
            }
            
            # Write metadata CSV
            with open(self.metadata_file, 'w', newline='') as f:
                writer = csv.writer(f)
                for key, value in metadata.items():
                    # Convert lists to semicolon-separated strings
                    if isinstance(value, list):
                        value = ';'.join(str(v) for v in value)
                    writer.writerow([key, value])
            
            self.metadata_written = True
            self.get_logger().info(f'Metadata written to {self.metadata_file}')

    def eeg_callback(self, msg: EEG):
        """Write EEG data to CSV, dynamically handling channel size"""
        if self.channel_size is None:
            self.get_logger().warn('Device info not received yet; skipping EEG data')
            return
        
        # Write header if file doesn't exist
        if not self.eeg_file.exists():
            with open(self.eeg_file, 'w', newline='') as f:
                writer = csv.writer(f)
                header = ['sec', 'nsec', 'session_id']
                header += [f'eeg_{i}' for i in range(self.channel_size)]
                header += [f'quality_{i}' for i in range(self.channel_size)]
                writer.writerow(header)
        
        # Prepare row
        row = [msg.header.stamp.sec, msg.header.stamp.nanosec, msg.session_id]
        row += list(msg.eeg)
        row += list(msg.quality)
        
        # Append row
        with open(self.eeg_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)
        
        self.message_count += 1
        if self.message_count % 100 == 0:
            self.get_logger().info(f'Saved {self.message_count} EEG messages to {self.eeg_file}')


def main(args=None):
    rclpy.init(args=args)
    eeg_saver = EEGRecorderCSV()
    
    try:
        rclpy.spin(eeg_saver)
    except KeyboardInterrupt:
        eeg_saver.get_logger().info(f'Shutting down. Total messages saved: {eeg_saver.message_count}')
    finally:
        eeg_saver.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
