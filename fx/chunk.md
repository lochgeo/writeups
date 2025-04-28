import fitz  # PyMuPDF
import json
import tiktoken

# 1. Load the PDF
doc = fitz.open("economic_report.pdf")

# 2. Setup tokenizer
enc = tiktoken.get_encoding("cl100k_base")  # OpenAI's tokenizer for ChatGPT, replace if using other LLMs

def num_tokens(text):
    return len(enc.encode(text))

# 3. Extract and chunk per page
chunks = []
chunk_size = 500  # tokens
overlap = 50      # optional token overlap for better context

for page_num in range(len(doc)):
    page = doc.load_page(page_num)
    text = page.get_text()
    
    # Split text into paragraphs
    paragraphs = text.split("\n\n")
    
    current_chunk = ""
    current_tokens = 0
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        tokens = num_tokens(para)
        
        # If adding this paragraph exceeds chunk size, save current and start new
        if current_tokens + tokens > chunk_size:
            chunks.append({
                "text": current_chunk.strip(),
                "page_number": page_num + 1
            })
            # Start a new chunk, optionally carry overlap
            if overlap > 0:
                # Take last few words from previous chunk
                overlap_text = ' '.join(current_chunk.split()[-overlap:])
                current_chunk = overlap_text + " " + para
                current_tokens = num_tokens(current_chunk)
            else:
                current_chunk = para
                current_tokens = tokens
        else:
            current_chunk += " " + para
            current_tokens += tokens
    
    # Save any leftover chunk
    if current_chunk.strip():
        chunks.append({
            "text": current_chunk.strip(),
            "page_number": page_num + 1
        })

# 4. Save to .jsonl
with open("economic_report.jsonl", "w", encoding="utf-8") as f:
    for chunk in chunks:
        json.dump(chunk, f)
        f.write("\n")

print(f"Saved {len(chunks)} chunks to economic_report.jsonl")