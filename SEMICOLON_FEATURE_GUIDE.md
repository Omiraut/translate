# Semicolon-Separated Translation Feature - Quick Reference

## Overview
The Translation API now supports translating multiple messages in a single request by separating them with semicolons (`;`).

## Basic Usage

### Syntax
```
message: "phrase1;phrase2;phrase3"
```

### Example
```bash
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello;Good morning;Welcome to India",
    "language": "hi"
  }'
```

## Response Format

### Batch Mode Response
```json
{
  "status": true,
  "code": 200,
  "message": "Translation successful",
  "data": {
    "converted_text": [
      {
        "original": "Hello",
        "translated": "नमस्ते",
        "cached": false,
        "library": "deep-translator"
      },
      {
        "original": "Good morning",
        "translated": "शुभ प्रभात",
        "cached": true
      },
      {
        "original": "Welcome to India",
        "translated": "भारत में आपका स्वागत है",
        "cached": false,
        "library": "deep-translator"
      }
    ],
    "language": "hi",
    "batch_mode": true,
    "total_phrases": 3,
    "cached_from_batch": 1
  }
}
```

## Key Features

### 1. **Automatic Whitespace Handling**
```
Input: " Hello ; Good morning ; Welcome "
→ Automatically trims spaces
Output: 3 phrases without leading/trailing spaces
```

### 2. **Empty Phrase Filtering**
```
Input: "Hello;;World"
→ Empty phrase is automatically filtered
Output: 2 phrases (Hello, World)
```

### 3. **Caching Integration**
- Each phrase is cached independently
- Repeated requests use cached translations
- Response shows which phrases were cached with `"cached": true/false`

### 4. **Metadata in Response**
| Field | Purpose |
|-------|---------|
| `batch_mode` | Indicates batch translation mode |
| `total_phrases` | Number of phrases translated |
| `cached_from_batch` | Count of phrases retrieved from cache |

## Comparison: Single vs Batch Mode

### Single Message
```json
PUT /translate
{
  "message": "Hello",
  "language": "hi"
}

Response data.converted_text: "नमस्ते" (string)
```

### Batch Mode
```json
PUT /translate
{
  "message": "Hello;World",
  "language": "hi"
}

Response data.converted_text: [
  { "original": "Hello", "translated": "नमस्ते", ... },
  { "original": "World", "translated": "दुनिया", ... }
] (array of objects)
```

## Edge Cases Handled

### ✅ Only Semicolons
```
Input: ";;;"
→ Error 400: "No valid phrases found"
```

### ✅ Leading/Trailing Semicolons
```
Input: ";Hello;World;"
→ Output: 2 phrases (empty at start/end filtered)
```

### ✅ Single Phrase with Semicolon
```
Input: "Hello;"
→ Output: 1 phrase (trailing empty filtered)
```

### ✅ Multiple Consecutive Semicolons
```
Input: "Hello;;;World"
→ Output: 2 phrases (empty phrases filtered)
```

## Performance Benefits

1. **Single API Call**: Translate multiple phrases with one request
2. **Network Efficiency**: Reduced HTTP overhead
3. **Cache Optimization**: Each phrase cached independently
4. **Scalability**: Handle bulk translations efficiently

## Example Use Cases

### 1. Multilingual Chat Messages
```json
{
  "message": "Hi there;How are you;Nice to meet you",
  "language": "hi"
}
```

### 2. Product Descriptions
```json
{
  "message": "Premium quality;Durable material;Best price",
  "language": "mr"
}
```

### 3. Greeting Messages
```json
{
  "message": "Welcome;Hello;Thank you;Goodbye",
  "language": "gu"
}
```

## Testing Examples

### Python Test
```python
import requests

response = requests.post(
    "http://localhost:8000/translate",
    json={
        "message": "Python;is;awesome",
        "language": "hi"
    }
)

data = response.json()
for item in data["data"]["converted_text"]:
    print(f"{item['original']} → {item['translated']}")
```

### JavaScript Test
```javascript
fetch('http://localhost:8000/translate', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    message: 'JavaScript;is;fun',
    language: 'hi'
  })
})
.then(r => r.json())
.then(data => {
  data.data.converted_text.forEach(item => {
    console.log(`${item.original} → ${item.translated}`);
  });
});
```

## Supported Languages

All existing language codes work with batch mode:
- `hi` - Hindi
- `mr` - Marathi
- `gu` - Gujarati
- `bn` - Bengali
- `ta` - Tamil
- `te` - Telugu
- `kn` - Kannada
- And more...

## Error Handling

### Invalid Input
```json
{
  "message": "Hello",
  "language": "invalid"
}
→ 400 Bad Request: "Unsupported language"
```

### Empty Message
```json
{
  "message": "",
  "language": "hi"
}
→ 400 Bad Request: "Message cannot be empty"
```

### All Semicolons (No Valid Phrases)
```json
{
  "message": ";;;",
  "language": "hi"
}
→ 400 Bad Request: "No valid phrases found"
```

## Monitoring & Statistics

Check `/stats` endpoint to monitor usage:
```bash
curl http://localhost:8000/stats
```

Response includes:
- `total_translations`: Total phrases translated
- `cache_stats`: Caching performance metrics

## Best Practices

1. **Use Semicolon for Related Phrases**: Group logically related messages
2. **Limit Batch Size**: Keep batch size reasonable for performance
3. **Monitor Cache**: Check stats to understand cache hit rates
4. **Error Handling**: Always check response status code
5. **Caching**: Leverage cache by requesting same phrases repeatedly
