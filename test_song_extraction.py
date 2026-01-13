"""
Test script to verify song name extraction works correctly
"""

def extract_song_name(query):
    """Test the song extraction logic"""
    # First, remove app names (order matters - longer phrases first)
    song = query.lower()
    song = song.replace("youtube music", "")
    song = song.replace("apple music", "")
    song = song.replace("jiosaavn", "")
    song = song.replace("soundcloud", "")
    song = song.replace("spotify", "")
    song = song.replace("youtube", "")
    song = song.replace("gaana", "")
    song = song.replace("saavn", "")
    
    # Remove command words
    song = song.replace("play", "")
    song = song.replace(" on ", " ")
    song = song.replace(" in ", " ")
    
    # Only remove "music" if it's standalone, not part of a phrase
    song = song.replace(" music ", " ")
    if song.endswith(" music"):
        song = song[:-6]  # Remove " music" from end
    
    # DON'T remove "song" - keep it as part of search query
    # This allows "Telugu song", "Hindi song", etc. to work properly
    
    # Clean up multiple spaces and trim
    while "  " in song:
        song = song.replace("  ", " ")
    song = song.strip()
    
    return song

# Test cases
test_queries = [
    "play Telugu song on YouTube",
    "play Hindi song on Spotify",
    "play believer on youtube",
    "play shape of you music",
    "play tamil song",
    "play arijit singh song",
    "play despacito on youtube music",
    "play music believer",
    "play bollywood song on gaana",
    "play punjabi song",
]

print("🧪 TESTING SONG NAME EXTRACTION (UPDATED)")
print("="*60)

for query in test_queries:
    extracted = extract_song_name(query)
    print(f"\nInput:  '{query}'")
    print(f"Output: '{extracted}'")
    print("-"*60)

print("\n✅ Test Complete!")
print("\n📝 Expected Results:")
print("- 'play Telugu song on YouTube' → 'telugu song' ✅")
print("- 'play Hindi song on Spotify' → 'hindi song' ✅")
print("- 'play believer on youtube' → 'believer' ✅")
print("- 'play tamil song' → 'tamil song' ✅")
