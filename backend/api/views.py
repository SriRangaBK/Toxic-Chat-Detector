from transformers import AutoTokenizer, AutoModelForSequenceClassification
from rest_framework.decorators import api_view
from rest_framework.response import Response
import torch

# Load English-only model (works with Roman Hindi)
model_name = "unitary/toxic-bert"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Hindi cuss words (Romanized)
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
    
    # Tokenize and predict using toxic-bert
    inputs = tokenizer(comment, return_tensors="pt", truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    probs = torch.sigmoid(outputs.logits)[0]

    # Toxicity labels as per the model
    labels = ["toxicity", "severe_toxicity", "obscene", "threat", "insult", "identity_hate"]
    result = {labels[i]: float(probs[i]) for i in range(len(labels))}
    flagged = {label: round(score, 4) for label, score in result.items() if score > 0.5}

    # Check for known Hindi cuss words (Romanized)
    cuss_word_flagged = contains_cuss_words(comment, cuss_words_hindi)

    # Final decision: any model or rule-based detection
    final_flagged = bool(flagged) or cuss_word_flagged

    return Response({
        "comment": comment,
        "toxicity_scores": {k: round(v, 4) for k, v in result.items()},
        "model_flagged": bool(flagged),
        "cuss_word_flagged": cuss_word_flagged,
        "final_flagged": final_flagged
    })
