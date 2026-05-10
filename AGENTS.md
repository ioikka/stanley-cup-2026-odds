# AGENTS.md — Infrastructure & Cross-Machine Context

## Devices

| Device | Hostname | IP | User | Access from rtxlinx |
|--------|----------|----|------|---------------------|
| **rtxlinx** | rtxlinx | 192.168.1.6 | ikka | Local (self) |
| **ser5** | ser5 | 192.168.1.5 / 94.157.122.90 (WAN, residential) | ikka | Direct SSH (`id_mcp` key, passwordless) |
| **vps-vless** | vps-ccfabebb | 135.125.199.120 / `2001:41d0:701:1100::c5c8` (OVH cloud) | debian | Direct SSH (`id_ed25519` key, passwordless) |

## SSH Access Matrix

| From → To | rtxlinx | ser5 | vps-vless |
|-----------|---------|------|-----------|
| **rtxlinx** | — | ✅ passwordless (`id_mcp`) | ✅ passwordless (`id_ed25519`) |
| **ser5** | ✅ passwordless (`id_mcp`) | — | ✅ direct (`id_ed25519`, no proxy needed) |

**SSH keys:**
- `id_mcp` — shared between rtxlinx ↔ ser5 (mcp-servers)
- `id_ed25519` — VPS access (vps-vless label, exists on both rtxlinx and ser5)
- `id_obnet` — localhost tunnel (port 9999/10000, ob-net / viktor)

**SSH config location:** `~/.ssh/config` on each machine

## ESPN Scraping & IP Considerations

- **Residential IPs work** — ser5 (94.157.122.90) can scrape ESPN successfully
- **Cloud IPs blocked** — VPS (OVH), GitHub Actions (Azure) all return 403 Forbidden
- **hockeystats.com works everywhere** — no cloud IP blocking, used as fallback source
- **Parser fallback chain:** ESPN → hockeystats.com → cached `data/odds.json`
- A hockeystats scrape counts as "live" data (exit code 0), so CI commits work

## SSH Config Tips

- All machines use `StrictHostKeyChecking no` for convenience
- VPS hostname `vps-vless` resolves via `/etc/hosts` on rtxlinx (`135.125.199.120`). ser5 uses the IP directly in its SSH config.
- To run commands on VPS from ser5: `ssh vps "command"`
- To run commands on ser5 from rtxlinx: `ssh ser5 "command"`
