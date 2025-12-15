# Loading Indicator & Search Debug Fixed 🔧

## Issues Found & Fixed

### Issue 1: JavaScript ID Mismatch
**Problem:** Loading overlay appeared but form wasn't submitting properly
**Cause:** JavaScript looking for `'platform-select'` ID but Django form didn't have it
**Fix:** Added `'id': 'platform-select'` to platform field in forms.py

### Issue 2: No Debug Output
**Problem:** Searches failing silently, no way to see what's wrong
**Cause:** No debug logging in views
**Fix:** Added comprehensive debug logging to track:
- Form submission
- Query validation
- API calls
- Results count
- Save operations
- Export operations

## Changes Made

### 1. Form ID Fix (`leads/forms.py`)
```python
# Before
platform = forms.ChoiceField(
    widget=forms.Select(attrs={
        'class': 'form-select'
    }),
)

# After
platform = forms.ChoiceField(
    widget=forms.Select(attrs={
        'class': 'form-select',
        'id': 'platform-select'  # ← Added this!
    }),
)
```

### 2. Debug Logging Added (`leads/views.py`)

**Google Maps Search:**
```python
print("DEBUG: Google search initiated")
print(f"DEBUG: Search query: {query}")
print("DEBUG: Calling search_places...")
print(f"DEBUG: Found {len(results)} results")
print(f"DEBUG: Auto-saving {len(saved_cafes)} cafés...")
print(f"DEBUG: Search error: {error}")
print(f"DEBUG: Form validation failed: {form.errors}")
```

**Apify Search:**
- Similar debug logging for TikTok/Instagram searches

## How to Debug Now

### 1. Watch Terminal Output

When you search, you'll see:

**Successful Search:**
```
DEBUG: Google search initiated
DEBUG: Search query: matcha café Tokyo
DEBUG: Calling search_places...
DEBUG: Found 20 results
DEBUG: Auto-saving 5 cafés with Instagram to Google Sheets
```

**Form Validation Error:**
```
DEBUG: Google search initiated
DEBUG: Form validation failed: {'query': ['This field is required.']}
```

**API Error:**
```
DEBUG: Google search initiated
DEBUG: Search query: test
DEBUG: Calling search_places...
DEBUG: Search error: Google Maps API error: INVALID_REQUEST
```

### 2. Check Browser Network Tab

- Open DevTools (F12)
- Go to Network tab
- Click "Search"
- Look for POST request
- Check response status (should be 200)
- Check response size (should be large if results found)

### 3. Verify API Keys

Make sure `.env` has:
```bash
GOOGLE_MAPS_API_KEY=your_key_here
APIFY_TOKEN=your_token_here
APIFY_ACTOR_TIKTOK=your_actor_id
APIFY_ACTOR_INSTAGRAM=your_actor_id
```

## Testing Steps

### Test Google Maps Search:

1. **Go to:** http://localhost:8000/google-search/
2. **Enter query:** "matcha café Tokyo"
3. **Click "Search"**
4. **Watch terminal for:**
   ```
   DEBUG: Google search initiated
   DEBUG: Search query: matcha café Tokyo
   DEBUG: Calling search_places...
   ```
5. **Wait for results**
6. **Check terminal for:**
   ```
   DEBUG: Found X results
   DEBUG: Auto-saving Y cafés with Instagram
   ```

### Test Apify Search:

1. **Go to:** http://localhost:8000/apify-search/
2. **Select:** TikTok
3. **Enter query:** "starbucks"
4. **Click "Search"**
5. **Watch terminal for debug output**
6. **Wait 10-30 seconds**
7. **Check for results**

## Common Issues & Solutions

### Issue: "Loading shows < 1 second but no data"

**Possible Causes:**
1. ❌ Form validation failing
2. ❌ API key missing/invalid
3. ❌ No results found
4. ❌ JavaScript error

**How to Check:**
- **Check terminal** for debug messages
- **Check browser console** (F12) for JavaScript errors
- **Check `.env`** file for API keys
- **Try different search query**

### Issue: "Form validation failed"

**Terminal shows:**
```
DEBUG: Form validation failed: {'query': ['This field is required.']}
```

**Solution:**
- Make sure input field has name="query"
- Check form is submitting correctly
- Verify CSRF token is present

### Issue: "API error"

**Terminal shows:**
```
DEBUG: Search error: REQUEST_DENIED
```

**Solution:**
- Check Google Maps API key is valid
- Verify API is enabled in Google Cloud Console
- Check billing is enabled

### Issue: "No Instagram found"

**Terminal shows:**
```
DEBUG: Found 20 results
Found 20 cafés but none had Instagram links.
```

**Solution:**
- This is normal! Not all places have Instagram
- Try different search terms
- Check if websites are accessible

## What to Look For

### ✅ Successful Search:
```
Terminal:
  DEBUG: Google search initiated
  DEBUG: Search query: matcha café Tokyo
  DEBUG: Calling search_places...
  DEBUG: Found 15 results
  DEBUG: Auto-saving 7 cafés with Instagram to Google Sheets
  DEBUG export_to_new_tab: Starting export of 7 cafés
  DEBUG export_to_new_tab: Tab name: matcha café Tokyo - Google Maps (1345)
  DEBUG export_to_new_tab: Export complete!

Browser:
  ✅ Found 15 results for "matcha café Tokyo"
  ✅ Auto-saved 7 café(s) with Instagram!
     Exported to: matcha café Tokyo - Google Maps (1345)
     [Open Sheet]
```

### ❌ Failed Search:
```
Terminal:
  DEBUG: Google search initiated
  DEBUG: Form validation failed: {'query': ['This field is required.']}

Browser:
  ❌ Please enter a valid search query.
```

## Next Steps

1. **Restart Django server** (if not auto-reloaded)
2. **Clear browser cache** (Cmd+Shift+R / Ctrl+F5)
3. **Try a search**
4. **Watch terminal output**
5. **Share debug output** if issues persist

## Files Modified

1. ✅ `leads/forms.py` - Added ID to platform select
2. ✅ `leads/views.py` - Added comprehensive debug logging

**Now you can see exactly what's happening during searches!** 🔍✅

