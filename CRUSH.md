# CRUSH.md - Letta AI Assistant

## Build & Development Commands
- `docker compose up -d` - Start Letta service
- `docker compose down` - Stop Letta service
- `docker compose logs letta` - View service logs
- `docker compose restart letta` - Restart service

## Code Style & Guidelines

### Docker/Container Configuration
- Use `letta/letta:latest` image
- Expose port 8283 internally, map to 8283 externally
- Configure Traefik labels for HTTPS routing
- Set all API keys via environment variables

### Environment Variables
- All AI service API keys are required: OPENAI_API_KEY, ANTHROPIC_API_KEY, GROQ_API_KEY, GEMINI_API_KEY
- Database connection via POSTGRES_URL with /letta suffix
- Enable self-hosted mode: LETTA_SELF_HOSTED=true
- Disable cloud redirect: LETTA_DISABLE_CLOUD_REDIRECT=true
- Set default view mode: LETTA_DEFAULT_VIEW_MODE=selfHosted

### Network Configuration
- Use external "proxy" network for Traefik routing
- Ensure proxy network exists before deployment

### Error Handling
- Container automatically restarts unless explicitly stopped
- Monitor logs for API connectivity issues
- Verify all required environment variables are set

### Naming Conventions
- Service name: "letta"
- Container name: "letta" 
- Hostname: letta.delo.sh (HTTPS)

## Key Configuration Notes
- OpenRouter used as OpenAI API provider
- PostgreSQL database required at DATABASE_URL
- All external API services require valid keys

💘 Generated with Crush