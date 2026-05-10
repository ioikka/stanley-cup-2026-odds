# AGENTS.md — Infrastructure & Cross-Machine Context

## Devices

### Local Network (192.168.1.0/24 — Dalfsen, NL)

| Device | Hostname | IP | User | Access from rtxlinx | Access from ser5 |
|--------|----------|----|------|---------------------|------------------|
| **rtxlinx** | rtxlinx | 192.168.1.6 | ikka | Local (self) | SSH (`id_mcp`, passwordless) |
| **ser5** | ser5 | 192.168.1.5 / 94.157.122.90 (WAN) | ikka | SSH (`id_mcp`, passwordless) | Local (self) |
| **gl66** | — | 192.168.1.66 | ikka | SSH (`id_mcp`) | — |
| **viktor** | — | 127.0.0.1:9999 (reverse tunnel) | ikka | SSH (`id_ed25519`, localhost tunnel) | SSH (`id_obnet`, port 10000) |

### Remote

| Device | Hostname | IP | User | Access from rtxlinx | Access from ser5 |
|--------|----------|----|------|---------------------|------------------|
| **vps-vless** | vps-ccfabebb | 135.125.199.120 (OVH cloud) | debian | SSH (`id_ed25519`, passwordless) | SSH direct (`id_ed25519`, passwordless) |

## SSH Access Matrix

| From → To | rtxlinx | ser5 | vps-vless | viktor | gl66 |
|-----------|---------|------|-----------|--------|------|
| **rtxlinx** | — | ✅ `id_mcp` | ✅ `id_ed25519` | ✅ `id_ed25519` (port 9999) | ✅ `id_mcp` |
| **ser5** | ✅ `id_mcp` | — | ✅ `id_ed25519` | ✅ `id_obnet` (port 10000) | — |
| **viktor** | 🔁 reverse tunnel (rtx) | 🔁 reverse tunnel (ser5) | — | — | — |
| **vps-vless** | — | — | — | — | — |

## SSH Keys

| Key | Comment | Used For |
|-----|---------|----------|
| `id_mcp` | mcp-servers | rtxlinx ↔ ser5, rtxlinx → gl66 |
| `id_ed25519` | vast-ai-key (ser5) / vps-vless (rtxlinx) | VPS access (different keypair per machine) |
| `id_obnet` | ser5→viktor tunnel auth | ser5 → viktor (port 10000) |
| `id_ed25519_tunnel` | viktor→ser5 reverse tunnel | viktor systemd service |
| `id_ed25519_tunnel_rtx` | viktor→rtx reverse tunnel | viktor systemd service |
| `id_github` | rtxlinx-local-ai | GitHub |

## Network Details

- **ISP:** Odido Netherlands (AS50266), Public IP: 94.157.122.90
- **rtxlinx:** Local AI server, runs vLLM (`http://192.168.1.6:8000/v1`)
- **ser5:** Home server, runs Docker services (relay-xray, Home Assistant, monitoring)
- **viktor:** Ubuntu 18.04 in Moscow Oblast (AS5969), reverse SSH tunnels to both rtxlinx (port 9999) and ser5 (port 10000). Outbound-only (CGNAT).

## VPN / Tunnel Topology

```
viktor (Moscow, CGNAT)
  ├─ reverse SSH tunnel ─→ rtxlinx:9999 (access as `ssh viktor` from rtxlinx)
  └─ reverse SSH tunnel ─→ ser5:10000  (access as `ssh viktor` from ser5)

ser5:51236 ── VLESS+REALITY relay ──→ vps-vless (OVH)
```

## SSH Config Tips

- All machines use `StrictHostKeyChecking no` for convenience
- VPS hostname `vps-vless` resolves via `/etc/hosts` on rtxlinx. ser5 uses the IP directly.
- To run commands on VPS from ser5: `ssh vps "command"`
- To run commands on ser5 from rtxlinx: `ssh ser5 "command"`
