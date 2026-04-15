# 🌐 Wake on LAN Pro for ComfyUI

A powerful custom node for ComfyUI to wake up remote machines via Magic Packets (WOL), resolve their IP addresses efficiently, and monitor their online status.

## Features
- **Multi-MAC Support**: Process lists of MAC addresses (separated by commas or newlines).
- **Session Memory**: Prevents redundant Magic Packets by tracking awakened devices during the current session.
- **Smart IP Resolution**: Resolves IP addresses for MACs instantly using a UDP-trigger + ARP-table lookup — **no slow network sweeps**.
- **Status Visualization**: Clear feedback with icons:
  - ✅ Magic Packet sent successfully / IP found.
  - ℹ️ Device already awakened in this session (Skipped).
  - ❌ IP resolution failed.
- **Safety Stop**: The entire ComfyUI workflow stops immediately (throws exception) if a timeout occurs or an invalid MAC is detected.
- **Zero Dependencies**: Uses only the Python Standard Library (no pip installs required).

## Installation
1. Navigate to your ComfyUI `custom_nodes` folder.
2. Create a new folder named `ComfyUI-WOL`.
3. Place `__init__.py` and `wol_node.py` into this folder.
4. Restart ComfyUI.

## Standalone Usage & Execution
- **Mandatory Ports**: None. This node is fully functional **standalone**. All required data is entered via the internal widgets (text fields/dropdowns).
- **Execution**: ComfyUI will execute this node during the "Queue Prompt" even if no input/output ports are connected. 
- **Workflow Control**: To ensure the rest of your workflow waits for this node (especially when using `check_online`), it is recommended to connect the `online_status` output to a "Show Text" node or use it as a string input for subsequent nodes.

## How Smart IP Resolution Works
Instead of scanning the whole subnet, this node uses a clever Layer-2 trick:
1. It sends an empty UDP broadcast to the network.
2. Active devices respond on the Ethernet level, which automatically updates your PC's internal **ARP cache**.
3. The node reads the IP address directly from this table. This is extremely fast and resource-friendly.

## Parameters
- **mac_addresses**: List of physical addresses (e.g., `00:11:22:33:44:55`).
- **mode**: `once_per_session` (Default) or `always`.
- **resolve_ips**: Enables automatic IP discovery for the given MACs.
- **check_online**: Pauses the workflow and pings the `ip_for_ping` until it responds.
- **timeout_seconds**: Time limit for the online check (Default: 60s). Triggers a safety stop if exceeded.

## Outputs
- **wol_status**: List of sent packets with status icons.
- **online_status**: Confirmation if the target IP is reachable.
- **discovered_ips**: Multi-line list of resolved MAC-to-IP mappings.

*Tip: Use a "Show Text" node to monitor the outputs directly in the UI.*
