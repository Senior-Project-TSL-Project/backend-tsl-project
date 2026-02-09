import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from ..config import MODEL_PATH, PREFIX_TEXT, MAX_LENGTH, DEVICE


class ModelService:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = DEVICE
        
    def load_model(self) -> None:
        print(f"🚀 Loading model from {MODEL_PATH}...")
        print(f"📱 Using device: {self.device}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(str(MODEL_PATH))
        self.model = AutoModelForSeq2SeqLM.from_pretrained(str(MODEL_PATH))
        self.model.to(self.device)
        self.model.eval()
        
        print("✅ Model loaded successfully!")
    
    def unload_model(self) -> None:
        print("🧹 Cleaning up model resources...")
        del self.model
        del self.tokenizer
        self.model = None
        self.tokenizer = None
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    @property 
    def is_loaded(self) -> bool:
        return self.model is not None and self.tokenizer is not None
    
    def predict_gloss(self, text: str) -> tuple[str, float]:
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        self.model.eval()

        # Tokenize input text and move tensors to the selected device
        inputs = self.tokenizer(
            PREFIX_TEXT + text,
            return_tensors="pt",
            padding=True
        ).to(self.device)

        # Generate output sequence
        with torch.no_grad():
            outputs = self.model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=MAX_LENGTH,
                num_beams=5,           
                early_stopping=True,
                return_dict_in_generate=True,
                output_scores=True
            )

        # Decode generated token IDs into text
        prediction = self.tokenizer.decode(
            outputs.sequences[0],
            skip_special_tokens=True
        )

        # Estimate confidence score
        logits = torch.stack(outputs.scores, dim=1)
        probs = F.softmax(logits, dim=-1)

        token_probs = torch.gather(
            probs,
            2,
            outputs.sequences[:, 1:].unsqueeze(-1)
        )

        confidence = token_probs.mean().item() * 100

        return prediction, confidence


# Global model service instance
model_service = ModelService()
