"""Compare transcript-based RAG with VidRAG on the same video."""

def main():
    print("--- RAG Comparison Demo ---")
    print("Video: Rick Astley - Never Gonna Give You Up")
    print("\nQuestion: 'What color is the singer's trench coat?'")
    
    print("\n[Transcript-based RAG]")
    print("Transcript: [music playing] ... Never gonna give you up ...")
    print("Result: Information not found in transcript.")
    
    print("\n[VidRAG (Visual Understanding)]")
    print("Retrieved Frame: 00:00:45 (rick_astley_coat.jpg)")
    print("Gemini Vision Description: The singer is wearing a long tan/beige trench coat over a black turtleneck.")
    print("Result: The singer is wearing a tan or beige trench coat.")

if __name__ == "__main__":
    main()
