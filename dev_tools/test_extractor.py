from extractors import ExtractorFactory

sources = ["otakudesu"]

for source_name in sources:
    print(f"\n{'='*20}")
    print(f"Testing Source: {source_name}")
    print(f"{'='*20}")
    
    extractor = ExtractorFactory.get_extractor(source_name)
    if not extractor:
        print(f"Extractor {source_name} not found")
        continue

    print("Testing Search...")
    query = "naruto"
    results = extractor.search(query)
    
    if results:
        print(f"Found {len(results)} results.")
        print(f"First result: {results[0]}")
        
        print("\nTesting Episodes...")
        episodes = extractor.get_episodes(results[0]['url'])
        if episodes:
            print(f"Found {len(episodes)} episodes.")
            # Test first and last episode to be sure
            print(f"First episode: {episodes[0]}")
            
            print("\nTesting Stream (First Episode)...")
            stream = extractor.get_stream_url(episodes[0]['url'])
            print(f"Stream data: {stream}")
        else:
            print("No episodes found.")
    else:
        print("No results found.")
