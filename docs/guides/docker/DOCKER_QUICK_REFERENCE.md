# FFXI Server Docker Setup - Quick Reference

This document provides a quick reference for the Docker setup implemented for the FFXI Server.

## Quick Start

```bash
# Clone and setup
git clone https://github.com/mupoese/FFXI-Server.git
cd FFXI-Server

# Configure environment
cp .env.example .env
# Edit .env with your database passwords

# Start server
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f ffxi-server
```

## Server Access

| Service | URL/Port | Description |
|---------|----------|-------------|
| Game Login | `localhost:54001` | FFXI Client connection |
| Game Data | `localhost:54230` | Main game data port |
| Search | `localhost:54002` | Player/linkshell search |
| Admin Panel | `http://localhost:8088` | Web management interface |
| Database Admin | `http://localhost:8080` | PhpMyAdmin (with --profile admin) |

## Docker Services

- **ffxi-server**: Main FFXI server container with all game components
- **db**: MariaDB database for game data
- **cloudflare-tunnel**: Optional Cloudflare tunnel for external access
- **redis**: Optional caching service
- **phpmyadmin**: Optional database management interface

## Cloudflare Tunnel Setup

1. Create tunnel in [Cloudflare Zero Trust](https://one.dash.cloudflare.com/)
2. Add tunnel token to `.env`:
   ```env
   CLOUDFLARE_TUNNEL_TOKEN=your_tunnel_token_here
   CLOUDFLARE_DOMAIN=yourdomain.com
   ```
3. Start with Cloudflare:
   ```bash
   docker-compose --profile cloudflare up -d
   ```

## FFXI Network Ports

### Required Ports (TCP/UDP)
- **54001** - Login View (TCP)
- **54002** - Search Service (TCP)
- **54230** - Login Data/Map (TCP/UDP)
- **54231** - Login Auth (TCP)
- **51220** - Login Config (TCP)
- **54003** - ZMQ Messaging (TCP)
- **8088** - HTTP Admin (TCP)

### Database
- **3306** - MariaDB (TCP)

## Troubleshooting

### Build Issues
```bash
# Rebuild completely
docker-compose build --no-cache
docker-compose up -d

# Check logs
docker-compose logs ffxi-server
```

### Database Issues
```bash
# Reset database
docker-compose down -v
docker-compose up -d

# Access database directly
docker-compose exec db mysql -u root -p
```

### Cloudflare Issues
- Ensure tunnel token is valid
- Check domain DNS configuration
- Note: UDP traffic requires Cloudflare Spectrum

## Development

### Building Custom Image
```bash
# Build only
docker build -t custom-ffxi-server .

# Test build stages
docker build --target build-stage -t ffxi-build-test .
```

### Volume Management
```bash
# Backup data
docker run --rm -v ffxi-server_db_data:/data -v $(pwd):/backup alpine tar czf /backup/db-backup.tar.gz -C /data .

# Restore data
docker run --rm -v ffxi-server_db_data:/data -v $(pwd):/backup alpine sh -c "cd /data && tar xzf /backup/db-backup.tar.gz"
```

## Security Notes

- Change default passwords in `.env`
- Use HTTPS in production with Cloudflare tunnel
- Consider VPN for UDP game traffic
- Regular backups of database volumes

## Support

For issues and documentation, see:
- Main README.md for detailed setup
- Docker logs for debugging
- FFXI community wikis for game-specific help