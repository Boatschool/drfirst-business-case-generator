# API Rate Limiting Implementation

## Overview

This document describes the implementation of basic API rate limiting for the DrFirst Business Case Generator backend API using the `slowapi` library.

## Implementation Details

### Library Used

- **slowapi**: A rate limiting library for FastAPI/Starlette applications
- Version: 0.1.9
- GitHub: https://github.com/laurents/slowapi

### Configuration

Rate limiting is configured through environment variables:

```bash
# Default rate limit for most endpoints
DEFAULT_RATE_LIMIT=100/minute

# Burst rate limit for strict control on sensitive endpoints  
BURST_RATE_LIMIT=20/second

# Optional Redis URL for distributed rate limiting
REDIS_URL=redis://localhost:6379/0
```

### Rate Limiting Strategy

#### Key Function
The rate limiter uses a hybrid key function that:
1. **Authenticated users**: Uses user ID from Firebase Auth token (`user:12345`)
2. **Unauthenticated requests**: Falls back to IP address (`ip:192.168.1.1`)

This ensures:
- Fair limits per authenticated user across devices
- IP-based protection for public endpoints
- Prevents shared IP issues (e.g., corporate networks)

#### Storage
- **Development**: In-memory storage (default, per-instance)
- **Production**: Redis storage (recommended for multi-instance deployments)
- **Fallback**: Gracefully falls back to in-memory if Redis is unavailable

### Applied Rate Limits

| Endpoint | Rate Limit | Reasoning |
|----------|------------|-----------|
| `/api/v1/cases` (GET) | 50/minute | Moderate limit for listing operations |
| `/api/v1/cases/{id}` (GET) | 30/minute | Stricter limit for detailed views |
| `/api/v1/agents/generate` (POST) | 5/minute | Very strict - resource intensive |
| `/api/v1/agents/status/{id}` (GET) | 20/minute | Moderate limit for status checks |
| Other endpoints | 100/minute | Default rate limit |

### Error Responses

When rate limits are exceeded, the API returns:

```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again later.",
  "detail": "1 per 1 minute",
  "type": "rate_limit_exceeded"
}
```

**HTTP Status**: 429 Too Many Requests  
**Headers**:
- `Retry-After`: Seconds until requests are allowed again
- `X-RateLimit-Limit`: The configured rate limit

### Files Modified

1. **requirements.txt**: Added `slowapi==0.1.9` and `aiohttp==3.10.11`
2. **app/core/config.py**: Added rate limiting configuration settings
3. **app/middleware/rate_limiter.py**: New middleware module with rate limiting logic
4. **app/main.py**: Integrated rate limiter with FastAPI app
5. **.env.template**: Added rate limiting environment variables
6. **api/v1/cases/list_retrieve_routes.py**: Applied rate limits to case endpoints
7. **api/v1/agent_routes.py**: Applied strict rate limits to generation endpoints

### Testing

Use the provided test script to verify rate limiting:

```bash
# Install test dependencies
pip install aiohttp

# Run the test script (with backend running)
python test_rate_limiting.py
```

The test script will:
1. Send rapid requests to various endpoints
2. Verify that 429 responses are returned when limits are exceeded
3. Analyze and report rate limiting effectiveness

### Production Considerations

#### Redis Setup
For production deployments with multiple instances, configure Redis:

```bash
# Google Cloud Memorystore example
REDIS_URL=redis://10.0.0.1:6379/0

# Or Redis Cloud
REDIS_URL=redis://username:password@host:port/db
```

#### Monitoring
Monitor rate limiting effectiveness through:
- Application logs (rate limit events are logged)
- HTTP 429 response metrics
- Redis memory usage (if using Redis storage)

#### Tuning Rate Limits
Adjust rate limits based on:
- User behavior analysis
- System resource capacity
- Business requirements

Common adjustments:
```bash
# More restrictive for abuse prevention
DEFAULT_RATE_LIMIT=50/minute

# More permissive for high-traffic legitimate usage
DEFAULT_RATE_LIMIT=200/minute

# Per-endpoint customization in code
@limiter.limit("10/minute")  # Very strict
@limiter.limit("1000/hour")  # Hourly limit
```

### Security Benefits

1. **DDoS Protection**: Prevents overwhelming the API with requests
2. **Resource Conservation**: Protects expensive operations (AI generation)
3. **Fair Usage**: Ensures equitable access across users
4. **Abuse Prevention**: Limits automated scraping and abuse

### Limitations

1. **Per-Instance Storage**: Without Redis, limits are per-server instance
2. **Shared IPs**: Corporate networks may hit IP-based limits faster
3. **Clock Skew**: Distributed deployments may have slight timing differences

### Future Enhancements

1. **Dynamic Rate Limits**: Adjust limits based on user tier/subscription
2. **Whitelist/Blacklist**: Special handling for trusted IPs or problem users
3. **Rate Limit Analytics**: Dashboard for monitoring rate limit patterns
4. **Quota Systems**: Monthly/daily quotas in addition to per-minute limits

## Troubleshooting

### Common Issues

**Rate limits not working:**
- Check that `slowapi` is installed
- Verify rate limiter is attached to app state
- Ensure exception handler is registered

**429 errors for legitimate users:**
- Check if rate limits are too strict
- Verify user ID extraction is working
- Consider IP-based issues for shared networks

**Redis connection errors:**
- Verify Redis URL configuration
- Check network connectivity to Redis instance
- Rate limiter will fall back to in-memory storage

### Debugging

Enable debug logging to see rate limiting in action:

```python
import logging
logging.getLogger("app.middleware.rate_limiter").setLevel(logging.DEBUG)
```

This will log:
- Rate limiting key used for each request
- Storage type (Redis vs in-memory)
- Rate limit configuration details 