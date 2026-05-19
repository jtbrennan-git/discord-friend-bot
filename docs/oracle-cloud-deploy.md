# Oracle Cloud Always Free Deploy

This runs Discord Friend Bot plus the optional Hermes harness on an Oracle Cloud Always Free Ampere VM.

Oracle's Always Free Ampere A1 allowance is equivalent to 4 OCPUs and 24 GB memory total for an Always Free tenancy. Stay at or below that allowance and avoid paid add-ons.

Source: https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm

## 1. Create The VM

In Oracle Cloud:

1. Create a compute instance.
2. Use an Always Free eligible shape: `VM.Standard.A1.Flex`.
3. Recommended size for this bot: `1 OCPU`, `6 GB RAM`.
4. Use Ubuntu 22.04 or 24.04.
5. Keep the boot volume modest, for example `50 GB`.
6. Add your SSH public key.

You do not need to expose inbound web traffic for Discord gateway operation. SSH is enough. The app binds health checks to localhost in Docker Compose.

## 2. Install Docker

SSH into the VM:

```bash
ssh ubuntu@<oracle-vm-public-ip>
```

Install Docker:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl git
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker "$USER"
```

Log out and back in so the Docker group applies.

## 3. Deploy The Bot

Clone the repo:

```bash
git clone https://github.com/jtbrennan-git/discord-friend-bot.git
cd discord-friend-bot
```

Create `.env`:

```bash
cp .env.example .env
nano .env
```

At minimum, set:

```env
DISCORD_TOKEN=
LLM_API_KEY=
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=openrouter/owl-alpha
ADMIN_USER_IDS=
CONTROL_ADMIN_IDS=
TARGET_GUILD_ID=
HERMES_ENABLED=true
HERMES_PROVIDER=openrouter
HERMES_MODEL=openrouter/owl-alpha
HERMES_ADMIN_TOOLSETS=all
```

Start it:

```bash
mkdir -p data
docker compose -f docker-compose.oracle.yml up -d --build
```

Check logs:

```bash
docker compose -f docker-compose.oracle.yml logs -f
```

## 4. Test Hermes

In Discord, as a user listed in `ADMIN_USER_IDS` or `CONTROL_ADMIN_IDS`:

```text
!admin ask say exactly: hermes-ok
```

Then test a tool/code request:

```text
!admin ask write snake in python and print the code
```

## 5. Stop Fly To Avoid Double Running

Once Oracle is confirmed working, stop the Fly app so only one bot process is connected:

```bash
flyctl scale count 0 -a friend-bot-7214
```

If you want to keep Fly as rollback, leave its volume intact. If you want to remove ongoing Fly resources completely, delete the app and volume after backing up any data you need.

## Notes

- Do not create resources outside Always Free eligibility unless you accept charges.
- Keep only one running bot instance per Discord token.
- `./data` contains the local SQLite databases, logs, and Hermes profile state.
- Back up `./data` before replacing the VM.
