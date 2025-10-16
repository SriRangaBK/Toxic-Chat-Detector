from transformers import AutoTokenizer, AutoModelForSequenceClassification
from rest_framework.decorators import api_view
from rest_framework.response import Response
import torch # Still required for the model inference, but hopefully the smaller model is manageable.

# --- MODIFIED: Switched to a lighter, smaller model base (DistilBERT) ---
# NOTE: This model is only for general sentiment/classification, not specifically multi-label toxicity like the original.
#       Finding a direct replacement with the exact 6 labels that is small enough is difficult.
#       For demonstration, we use a general DistilBERT, which often uses fewer labels.
#       You will need to adjust the labels and scoring to match the model you choose.
model_name = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# --- Original custom cuss word list ---
cuss_words_hindi = {
    "bhenchod", "madarchod", "chutiya", "randi", "saala", "harami",
    "lavda", "gandu", "chodu", "bhadwa", "kutte", "randwa", "lund",
    "chhakke", "hijra", "chusle", "behenchod", "ullu", "kamina", "nalayak",
    "bewakoof", "nikamma", "pagal", "gavar", "gadha", "bakchod", "chutiyapa",
    "lofer","bevarsi","bolimagne","hucha","lowde","nin amman","nin akkan","keyya",
    "sule","munde"
}

def contains_cuss_words(text, cuss_set):
    text = text.lower()
    return any(word in text for word in cuss_set)

@api_view(['POST'])
def check_comment(request):
    comment = request.data.get("comment", "")
    
    # Tokenize and predict using the new, lighter model
    inputs = tokenizer(comment, return_tensors="pt", truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    
    # --- MODIFIED: Simplified scoring logic to match a binary classification model (like SST-2) ---
    # The new model typically outputs logits for two classes (e.g., NEGATIVE, POSITIVE)
    # We will treat the "negative" score as the "flagged" score.
    
    # 1. Get the class predictions
    probabilities = torch.softmax(outputs.logits, dim=1).squeeze().tolist()
    
    # 2. Map predictions (assuming a simple binary negative/positive output)
    # Class 0 is typically Negative/Toxic for sentiment models.
    # NOTE: You MUST check the exact label mapping for the model you choose.
    
    # Assuming a simplified check:
    score = probabilities[0] if len(probabilities) > 1 else 0.0
    
    # We use a threshold of 0.8 because a binary sentiment model is less direct than a toxicity model.
    model_flagged = score > 0.8
    
    # Prepare the result dictionary
    result = {"negative_score": score, "positive_score": probabilities[1] if len(probabilities) > 1 else 0.0}

    # --- Original rule-based check ---
    cuss_word_flagged = contains_cuss_words(comment, cuss_words_hindi)

    # Final decision: any model or rule-based detection
    final_flagged = model_flagged or cuss_word_flagged

    return Response({
        "comment": comment,
        # Display the simplified scores
        "toxicity_scores": {k: round(v, 4) for k, v in result.items()},
        "model_flagged": model_flagged,
        "cuss_word_flagged": cuss_word_flagged,
        "final_flagged": final_flagged
    })