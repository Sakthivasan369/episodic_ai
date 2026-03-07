from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
from sentence_transformers import SentenceTransformer, util
import torch

# Initialize models
# google/flan-t5-base for text-to-text generation (transforming titles)
model_id = "google/flan-t5-base"

try:
    # Explicitly load model and tokenizer to be safe
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
    
    # Try initializing the pipeline with 'text2text-generation'
    # If this fails, it's likely a missing dependency or task registry issue
    flan_t5 = pipeline("text2text-generation", model=model, tokenizer=tokenizer, device=-1)
except Exception as e:
    print(f"Warning: Failed to initialize 'text2text-generation' pipeline: {e}")
    # Fallback to a basic pipeline auto-inference if possible
    try:
        flan_t5 = pipeline(model=model_id, device=-1)
    except:
        flan_t5 = None

# sentence-transformers for semantic relevance check
similarity_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def generate_viral_title(original_title: str) -> str:
    """
    Uses FLAN-T5 to re-write a title into something more 'viral' 
    and verifies semantic relevance using all-MiniLM-L6-v2.
    """
    if not flan_t5:
        return f"Viral: {original_title}"

    # Prompt for FLAN-T5 to generate a clickworthy title
    prompt = f"Transform this story title into a viral, clickworthy TikTok title: {original_title}"
    
    # Generate candidates
    candidates = flan_t5(prompt, max_length=50, num_return_sequences=3, do_sample=True, temperature=0.9)
    
    original_embedding = similarity_model.encode(original_title, convert_to_tensor=True)
    
    best_title = original_title
    max_similarity = -1.0
    
    for candidate in candidates:
        candidate_text = candidate['generated_text'].strip()
        # Clean up common FLAN-T5 artifacts if any
        candidate_text = candidate_text.replace('"', '').replace("'", "")
        
        # Check similarity to original title to ensure it's not totally off-topic
        candidate_embedding = similarity_model.encode(candidate_text, convert_to_tensor=True)
        sim_score = util.pytorch_cos_sim(original_embedding, candidate_embedding).item()
        
        # We want something that is relevant but also different enough to be 'viral'
        if sim_score > max_similarity and candidate_text.lower() != original_title.lower():
            max_similarity = sim_score
            best_title = candidate_text

    return best_title

def enhance_series_with_hooks(series_data: dict) -> dict:
    """
    Generates viral titles and punchy hooks (< 10 words) for each episode.
    """
    if "episodes" not in series_data:
        return series_data

    for episode in series_data["episodes"]:
        original_title = episode.get("title", "Untitled")
        
        # 1. Generate Viral Title
        viral_title = generate_viral_title(original_title)
        episode["click_title"] = viral_title
        
        # 2. Refine Viral Hook (must be < 10 words)
        current_hook = episode.get("open_loop", "Watch to find out what happens next.")
        
        # If the hook is too long, we use FLAN-T5 to shorten it
        if flan_t5 and len(current_hook.split()) >= 10:
            shorten_prompt = f"Shorten this hook to less than 10 words, keep it mysterious: {current_hook}"
            short_hook_res = flan_t5(shorten_prompt, max_length=20)
            short_hook = short_hook_res[0]['generated_text'].strip()
            # Ensure it's actually shorter than 10 words
            if len(short_hook.split()) >= 10:
                short_hook = " ".join(short_hook.split()[:9]) + "..."
            episode["viral_hook"] = short_hook
        else:
            # Simple truncation if flan_t5 failed or not needed
            if len(current_hook.split()) >= 10:
                episode["viral_hook"] = " ".join(current_hook.split()[:9]) + "..."
            else:
                episode["viral_hook"] = current_hook
            
    return series_data
