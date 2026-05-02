# Raspberry Pi setup (headless)

Goal: get to the point where you can SSH from your laptop into the Pi, clone
this repo, run `scripts/hello_leds.py`, and watch real LEDs blink.

## What you'll need

- Raspberry Pi 4 (any RAM size)
- microSD card, 8 GB or larger (16 GB+ recommended)
- USB-C power supply (5 V / 3 A — the official one or equivalent)
- Wi-Fi network and the SSID + password
- A laptop on the same Wi-Fi network
- An SD card reader (built-in slot or USB adapter)

You will **not** need a monitor, keyboard, or mouse for path A. For path B
you'll need a one-time monitor + keyboard session on the Pi.

---

## Path A — re-image with headless from the start (recommended)

This is the cleanest way to get to a working headless Pi, especially the first
time. Reflashing the SD card wipes whatever's on it, so back up anything
important first.

### 1. Install Raspberry Pi Imager on your laptop

Download from <https://www.raspberrypi.com/software/>. macOS, Linux, and
Windows builds are all there.

### 2. Generate (or reuse) an SSH key on your laptop

If `ls ~/.ssh/id_ed25519.pub` works, you have one — skip ahead. Otherwise:

```sh
ssh-keygen -t ed25519 -C "luke@laptop"
# accept defaults; an empty passphrase is fine for a personal project
```

Now print the public key — you'll paste it into Imager in a moment:

```sh
cat ~/.ssh/id_ed25519.pub
```

### 3. Flash the SD card

1. Insert the SD card into your laptop.
2. Open Raspberry Pi Imager.
3. **Choose Device** → Raspberry Pi 4.
4. **Choose OS** → Raspberry Pi OS (64-bit) — pick the latest "Bookworm"
   release. The Lite variant is fine (and smaller); the Desktop one works too.
5. **Choose Storage** → your SD card.
6. Click **Next**, then **Edit Settings** when it asks about applying OS
   customisations. Set:
   - **General tab**
     - Hostname: `metroboard` (so the Pi will be reachable as
       `metroboard.local` over mDNS)
     - Username: `luke` (or whatever you want — match this everywhere below)
     - Password: pick something memorable (still useful as a fallback)
     - Configure wireless LAN: tick on, fill in your Wi-Fi SSID + password,
       Wireless LAN country = `US`
     - Set locale settings: tick on, timezone `America/Chicago`, keyboard `us`
   - **Services tab**
     - Enable SSH: tick on
     - **Use public-key authentication only** — paste the contents of
       `~/.ssh/id_ed25519.pub` here. (This is the safer option; password SSH
       is off.)
   - Save.
7. Confirm "Yes, apply OS customisation settings" → confirm erase → wait for
   write + verify (~5 min).
8. Eject the SD card.

### 4. First boot

1. Insert the SD card into the Pi.
2. Plug in the USB-C power supply.
3. Wait 1–2 minutes for first boot. The Pi expands the filesystem, joins
   Wi-Fi, and starts SSH.

### 5. SSH in from your laptop

```sh
ssh luke@metroboard.local
```

If `metroboard.local` doesn't resolve (some networks block mDNS), find the
IP from your router's admin page or with `arp -a | grep -i 'dc:a6:32\|b8:27:eb\|d8:3a:dd'`
(common Raspberry Pi MAC OUIs) and SSH to that IP instead.

You should land at a `luke@metroboard:~$` prompt. **Skip to "Once you're SSHed
in" below.**

---

## Path B — keep your existing install, convert it to headless

Use this if you don't want to re-image. It's a few more steps and assumes you
can connect a monitor + keyboard to the Pi for one session.

### 1. Boot the Pi with monitor + keyboard

Connect HDMI + USB keyboard, plug in power, log in.

### 2. Enable SSH and set the hostname

```sh
sudo raspi-config
```

- **System Options → Hostname** → set to `metroboard`
- **Interface Options → SSH** → enable
- **Localisation Options → WLAN Country** → `US` (if not already set)
- Finish, reboot when prompted.

If your Pi isn't on Wi-Fi yet, the easiest path on Bookworm:

```sh
sudo nmcli device wifi connect "YourSSID" password "YourPassword"
```

(On Bullseye or older, use `raspi-config` → Wireless LAN.)

### 3. Get the Pi's IP

```sh
hostname -I
```

Note the address (e.g. `192.168.1.42`).

### 4. Copy your SSH key from the laptop

On your **laptop** (not the Pi):

```sh
# only if you don't already have a key
ssh-keygen -t ed25519 -C "luke@laptop"

# replace the user@host with what you set above; metroboard.local should
# work, otherwise use the IP from step 3
ssh-copy-id luke@metroboard.local
```

You'll be prompted for the Pi user's password once; after this, key auth
works.

### 5. Disable SSH password auth (optional but recommended)

Once key auth works, on the Pi:

```sh
sudo sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart ssh
```

### 6. Unplug the monitor and keyboard

You're headless from here on. SSH in:

```sh
ssh luke@metroboard.local
```

---

## Once you're SSHed in

The remaining steps are the same regardless of which path you took.

### 1. Update the OS

```sh
sudo apt update
sudo apt full-upgrade -y
sudo reboot
```

Wait ~30 s, then SSH back in.

### 2. Install system packages we'll need

```sh
sudo apt install -y git python3-venv python3-lgpio
```

- `git` — to clone this repo
- `python3-venv` — for the virtualenv
- `python3-lgpio` — gpiozero's preferred pin-factory backend on Bookworm.
  Installing it system-wide and then giving the venv `--system-site-packages`
  is the simplest way to make it visible to the venv.

### 3. Confirm Python ≥ 3.11

```sh
python3 --version
```

Bookworm ships 3.11.x — you're good. If you somehow have an older OS with
Python < 3.11, the easiest fix is to re-image (Path A above).

### 4. Clone the repo and install

```sh
cd ~
git clone <your-repo-url> wego-metroboard
cd wego-metroboard
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

The `--system-site-packages` flag is what lets the venv see the
apt-installed `python3-lgpio`. Without it, gpiozero would fall back to a
less-preferred backend (or fail if none is available).

> If you haven't pushed this repo to a Git host yet, you can `scp -r` the
> directory from your laptop to the Pi instead:
> `scp -r /Users/luke/Code/wego-star-tracker luke@metroboard.local:~/wego-metroboard`

### 5. Smoke test in mock mode (no hardware required yet)

```sh
GPIOZERO_PIN_FACTORY=mock python scripts/hello_leds.py
```

You should see the same `[w→e] Riverfront (GPIO 17) ...` output you saw on
your laptop. This confirms the package imports cleanly on the Pi.

### 6. Hardware test

Once the breadboard is wired (see [`WIRING.md`](WIRING.md)):

```sh
python scripts/hello_leds.py
```

Real LEDs should now light in geographic order, west to east, then east to
west, then a 5-cycle Larson scan, then all 7 on for 2 s.

---

## Troubleshooting

**`ssh: Could not resolve hostname metroboard.local`**
mDNS isn't reaching the Pi. Find the IP from your router and SSH to that.
On macOS, `dns-sd -B _ssh._tcp` will list mDNS-advertised SSH hosts.

**`Permission denied (publickey)` on first SSH**
The public key didn't get baked into the image (path A) or `ssh-copy-id`
didn't run (path B). For path A, re-flash and double-check the Services tab
in Imager. For path B, re-run `ssh-copy-id`.

**`pip install` fails compiling something**
Most likely you skipped `sudo apt install python3-venv` or are missing
`build-essential`. `sudo apt install -y build-essential` covers most cases.

**`hello_leds.py` runs but no LEDs light**
Almost always a wiring issue, not software. See the troubleshooting section
in [`WIRING.md`](WIRING.md).

**`gpiozero.exc.BadPinFactory: Unable to load any default pin factory!`**
The venv can't see lgpio. Either you forgot `--system-site-packages` when
creating it, or `python3-lgpio` isn't installed. Run
`sudo apt install -y python3-lgpio`, then recreate the venv with
`python3 -m venv --system-site-packages .venv`.
