#!/bin/bash

# Translation API - cURL Examples
# Copy and paste any command into your terminal

echo "╔════════════════════════════════════════════════════════════╗"
echo "║       Translation API - cURL Examples                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Make sure the API is running: python main.py"
echo ""

BASE_URL="http://localhost:8000"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# HEALTH & INFO ENDPOINTS
# ============================================================================

echo -e "${BLUE}1. HEALTH CHECK${NC}"
echo "Command:"
echo "curl $BASE_URL/health"
echo -e "${GREEN}Response:${NC}"
curl -s "$BASE_URL/health" | python -m json.tool
echo ""

echo -e "${BLUE}2. GET SUPPORTED LANGUAGES${NC}"
echo "Command:"
echo "curl $BASE_URL/languages"
echo -e "${GREEN}Response:${NC}"
curl -s "$BASE_URL/languages" | python -m json.tool | head -30
echo "... (truncated, see full response)"
echo ""

# ============================================================================
# TRANSLATION EXAMPLES - INDIAN LANGUAGES
# ============================================================================

echo "╔════════════════════════════════════════════════════════════╗"
echo "║           TRANSLATION EXAMPLES - INDIAN LANGUAGES         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Hindi
echo -e "${BLUE}3. TRANSLATE TO HINDI${NC}"
echo "Command:"
echo "curl -X POST $BASE_URL/translate \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"message\": \"Good morning\", \"language\": \"hi\"}'"
echo -e "${GREEN}Response:${NC}"
curl -s -X POST "$BASE_URL/translate" \
  -H "Content-Type: application/json" \
  -d '{"message": "Good morning", "language": "hi"}' | python -m json.tool
echo ""

# Marathi
echo -e "${BLUE}4. TRANSLATE TO MARATHI${NC}"
echo "Command:"
echo "curl -X POST $BASE_URL/translate \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"message\": \"How are you?\", \"language\": \"mr\"}'"
echo -e "${GREEN}Response:${NC}"
curl -s -X POST "$BASE_URL/translate" \
  -H "Content-Type: application/json" \
  -d '{"message": "How are you?", "language": "mr"}' | python -m json.tool
echo ""

# Gujarati
echo -e "${BLUE}5. TRANSLATE TO GUJARATI${NC}"
echo "Command:"
echo "curl -X POST $BASE_URL/translate \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"message\": \"Thank you so much\", \"language\": \"gu\"}'"
echo -e "${GREEN}Response:${NC}"
curl -s -X POST "$BASE_URL/translate" \
  -H "Content-Type: application/json" \
  -d '{"message": "Thank you so much", "language": "gu"}' | python -m json.tool
echo ""

# Bengali
echo -e "${BLUE}6. TRANSLATE TO BENGALI${NC}"
echo "Command:"
echo "curl -X POST $BASE_URL/translate \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"message\": \"Welcome to our service\", \"language\": \"bn\"}'"
echo -e "${GREEN}Response:${NC}"
curl -s -X POST "$BASE_URL/translate" \
  -H "Content-Type: application/json" \
  -d '{"message": "Welcome to our service", "language": "bn"}' | python -m json.tool
echo ""

# ============================================================================
# TRANSLATION EXAMPLES - INTERNATIONAL LANGUAGES
# ============================================================================

echo "╔════════════════════════════════════════════════════════════╗"
echo "║          TRANSLATION EXAMPLES - INTERNATIONAL            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Spanish
echo -e "${BLUE}7. TRANSLATE TO SPANISH${NC}"
echo "Command:"
echo "curl -X POST $BASE_URL/translate \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"message\": \"Hello world\", \"language\": \"es\"}'"
echo -e "${GREEN}Response:${NC}"
curl -s -X POST "$BASE_URL/translate" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello world", "language": "es"}' | python -m json.tool
echo ""

# French
echo -e "${BLUE}8. TRANSLATE TO FRENCH${NC}"
echo "Command:"
echo "curl -X POST $BASE_URL/translate \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"message\": \"See you later\", \"language\": \"fr\"}'"
echo -e "${GREEN}Response:${NC}"
curl -s -X POST "$BASE_URL/translate" \
  -H "Content-Type: application/json" \
  -d '{"message": "See you later", "language": "fr"}' | python -m json.tool
echo ""

# ============================================================================
# CACHING DEMONSTRATION
# ============================================================================

echo "╔════════════════════════════════════════════════════════════╗"
echo "║               CACHING DEMONSTRATION                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo -e "${BLUE}9. FIRST REQUEST (NOT CACHED)${NC}"
echo "Command:"
echo "curl -X POST $BASE_URL/translate \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"message\": \"Cache test\", \"language\": \"hi\"}'"
echo -e "${GREEN}Response:${NC}"
RESPONSE1=$(curl -s -X POST "$BASE_URL/translate" \
  -H "Content-Type: application/json" \
  -d '{"message": "Cache test", "language": "hi"}')
echo "$RESPONSE1" | python -m json.tool
echo ""

echo -e "${BLUE}10. SECOND REQUEST (CACHED - FASTER)${NC}"
echo "Command (same as above):"
echo "curl -X POST $BASE_URL/translate \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"message\": \"Cache test\", \"language\": \"hi\"}'"
echo -e "${GREEN}Response (notice 'cached': true):${NC}"
RESPONSE2=$(curl -s -X POST "$BASE_URL/translate" \
  -H "Content-Type: application/json" \
  -d '{"message": "Cache test", "language": "hi"}')
echo "$RESPONSE2" | python -m json.tool
echo ""

# ============================================================================
# ERROR HANDLING
# ============================================================================

echo "╔════════════════════════════════════════════════════════════╗"
echo "║              ERROR HANDLING EXAMPLES                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo -e "${BLUE}11. EMPTY MESSAGE ERROR${NC}"
echo "Command:"
echo "curl -X POST $BASE_URL/translate \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"message\": \"\", \"language\": \"hi\"}'"
echo -e "${GREEN}Response (400 Error):${NC}"
curl -s -X POST "$BASE_URL/translate" \
  -H "Content-Type: application/json" \
  -d '{"message": "", "language": "hi"}' | python -m json.tool
echo ""

echo -e "${BLUE}12. INVALID LANGUAGE ERROR${NC}"
echo "Command:"
echo "curl -X POST $BASE_URL/translate \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"message\": \"Hello\", \"language\": \"xyz\"}'"
echo -e "${GREEN}Response (400 Error):${NC}"
curl -s -X POST "$BASE_URL/translate" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "language": "xyz"}' | python -m json.tool
echo ""

echo -e "${BLUE}13. MESSAGE TOO LONG ERROR${NC}"
echo "Command:"
echo "curl -X POST $BASE_URL/translate \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"message\": \"'$(printf 'x%.0s' {1..10001})'\", \"language\": \"hi\"}'"
echo -e "${GREEN}Response (400 Error):${NC}"
LONG_MESSAGE=$(printf 'x%.0s' {1..10001})
curl -s -X POST "$BASE_URL/translate" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"$LONG_MESSAGE\", \"language\": \"hi\"}" | python -m json.tool
echo ""

# ============================================================================
# SERVICE STATISTICS
# ============================================================================

echo "╔════════════════════════════════════════════════════════════╗"
echo "║            SERVICE STATISTICS & MANAGEMENT                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo -e "${BLUE}14. GET SERVICE STATISTICS${NC}"
echo "Command:"
echo "curl $BASE_URL/stats"
echo -e "${GREEN}Response:${NC}"
curl -s "$BASE_URL/stats" | python -m json.tool
echo ""

echo -e "${BLUE}15. CLEAR CACHE${NC}"
echo "Command:"
echo "curl -X POST $BASE_URL/cache/clear"
echo -e "${GREEN}Response:${NC}"
curl -s -X POST "$BASE_URL/cache/clear" | python -m json.tool
echo ""

# ============================================================================
# USEFUL ONE-LINERS
# ============================================================================

echo "╔════════════════════════════════════════════════════════════╗"
echo "║           USEFUL ONE-LINERS FOR SCRIPTING                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo "# Extract translated text only:"
echo "curl -s -X POST $BASE_URL/translate \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"message\": \"Hi\", \"language\": \"hi\"}' | jq -r '.data.converted_text'"
echo ""

echo "# Batch translation loop:"
echo "for lang in hi mr gu bn ta te kn ml; do"
echo "  echo \"Language: \$lang\""
echo "  curl -s -X POST $BASE_URL/translate \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"message\": \"Hello\", \"language\": \"'\"'\$lang'\"'\"}' | jq '.data.converted_text'"
echo "done"
echo ""

echo "# Check if API is up:"
echo "curl -s $BASE_URL/health | jq '.status'"
echo ""

echo "# Monitor in real-time:"
echo "watch -n 2 'curl -s $BASE_URL/stats | jq .'"
echo ""

# ============================================================================
# COMPLETION
# ============================================================================

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                  EXAMPLES COMPLETED                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📚 For more examples, see:"
echo "   • API_DOCUMENTATION.md"
echo "   • README.md"
echo "   • QUICKSTART.md"
echo ""
echo "🌐 Interactive API Documentation:"
echo "   http://localhost:8000/docs"
echo ""
