# Home Assistant GSM Call

[![Add a custom repository to HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=tbutiu&repository=homeassistant-gsm-call&category=integration)

Home Assistant integration that allows you to make voice calls and send SMS messages using 3G/4G/LTE USB modems.

This version includes critical stability fixes for Huawei modems, including buffer clearing sequences (`\x1B`) and asynchronous timing adjustments to prevent serial timeouts.

## Installation

This integration is best installed via **HACS**:

1. Open **HACS** → **Integrations**.
2. Click the three dots (⋮) in the top right → **Custom repositories**.
3. Repository: `tbutiu/homeassistant-gsm-call` | Category: **Integration**.
4. Click **Add**, then find and install **GSM Call**.
5. Restart Home Assistant.

## Configuration

Add the following to your `configuration.yaml`. For Huawei modems, we recommend using the specific interface paths identified in your hardware.

### Voice Call Configuration
Used for emergency alerts or triggering automations (e.g., heating control).

```yaml
notify:
  - name: call_centrala
    platform: gsm_call
    # Usually if00 is the voice interface for Huawei E352/E171
    device: /dev/serial/by-id/usb-HUAWEI_HUAWEI_Mobile-if00-port0
    dial_timeout_sec: 20
    call_duration_sec: 30
```

### SMS Configuration

Note: For maximum stability, use a separate notify entry. You can use the same device path or the PC UI interface (`if02`) if available.

```yaml
notify:
  - name: sms_alerta
    platform: gsm_call
    type: sms
    device: /dev/serial/by-id/usb-HUAWEI_HUAWEI_Mobile-if00-port0
```

## Usage

### Action: Make a Call

```yaml
action: notify.call_centrala
data:
  target: "+407XXXXXXXX"
  message: "Not used for voice but required by HA"
```

### Action: Send SMS

```yaml
action: notify.sms_alerta
data:
  target: "+407XXXXXXXX"
  message: "System: Centrala a fost pornita!"
```

## Events

The integration fires the `gsm_call_ended` event. You can use this to trigger actions based on whether you answered or declined the call.

**Example: Turn on heating when a call from owner is declined (Zero cost trigger)**

```yaml
automation:
  - alias: "Control Centrala via Missed Call"
    trigger:
      - platform: event
        event_type: gsm_call_ended
        event_data:
          reason: "declined"
          phone_number: "+407XXXXXXXX"
    action:
      - action: switch.turn_on
        target:
          entity_id: switch.releu_centrala
```

## Supported Hardware

Tested and verified:

* **Huawei E352** (Orange Romania) - *Full support*
* **Huawei E1550 / E171 / E173**
* **ZTE MF192** (requires `hardware: zte`)
* **Globetrotter HSUPA** (requires `hardware: gtm382`)

## Troubleshooting & Tips

### Proxmox Users

If running Home Assistant in a VM, ensure the USB controller is set to **USB 2.0** (not 3.0) to avoid serial timing issues and timeouts.

### Modem "Busy" or "Timeout"

If the modem stops responding, it might be stuck in a command prompt (e.g., `>`). Recent versions send an Escape character (`\x1B`) before each command to clear the buffer automatically.

### Manual SMSC Check

Ensure your SMS Center (SMSC) number is correct. For Orange Romania, it should be `+40744946000`.

```bash
# Verify via terminal
echo -e "AT+CSCA?\r" > /dev/serial/by-id/usb-HUAWEI_HUAWEI_Mobile-if00-port0
```
