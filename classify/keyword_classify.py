#conding:utf-8
import sys
sys.path.insert(0, "../../")
sys.path.insert(0, "../../Buaanlp_policy/")
import jieba
import os
from Buaanlp_policy.common import Params
from Buaanlp_policy.data import get_vocab_from_files
from Buaanlp_policy.data.dataset_readers import TextClassificationJsonReader
from Buaanlp_policy.models.classify import TextcnnClassifier, TextcnnScorer
from Buaanlp_policy.data.dataset_readers import BertClassificationJsonReader
from Buaanlp_policy.models.classify import Bert_freeze_model, BertFreezeScorer
from Buaanlp_policy.data.tokenizers import WhitespaceTokenizer, BertTokenizer
from copy import deepcopy
current_path = os.path.dirname(os.path.abspath(__file__))
print(current_path)

class CnnKeywordClassify():
    def __init__(self):
        vocab_config = {
            "vocab_file": os.path.join(current_path, "model", "word2vec", "policy_vocab.txt"),
            "label_file": os.path.join(current_path, "model", "keyword", "policy_keyword_label.txt"),
            "oov_token": "[UNK]",
            "padding_token": "[PAD]"
        }

        model_config = {
            "embedding": {
                "pretrained_file": os.path.join(current_path, "model", "word2vec", "policy_vec_300.txt"),
                "embedding_dim": 300,
                "trainable": True,
            },
            'encoder': {
                'embedding_dim': 300,
                'num_filters': 60,
                'ngram_filter_sizes': (1, 2, 3, 4)
            },
            'dropout': 0.1,
        }

        DataLoadConfig = {
            "tokenizer": WhitespaceTokenizer(),
            "max_sequence_length": 100,
            "lazy": False
        }
        vocab = get_vocab_from_files(**vocab_config)
        reader = TextClassificationJsonReader.from_params(params=Params(DataLoadConfig))
        self.model = TextcnnScorer.from_params(params=Params(deepcopy(model_config)), dataset_reader=reader, \
                                          model_path=os.path.join(current_path, "model", "keyword", "best.th"), sentence_size=100, vocab=vocab)

    def predict(self, sentence):
        sentence = " ".join(list(jieba.cut(sentence)))
        results = self.model.predict(sentence)
        return results

    def predicts(self, sentences):
        sentences = [" ".join(list(jieba.cut(sentence))) for sentence in sentences]
        results = self.model.predict_batch(sentences)
        return results

class BertKeywordClassify():
    def __init__(self):
        vocab_config = {
            "vocab_file": os.path.join(current_path, "model", "bert", "vocab.txt"),
            "label_file": os.path.join(current_path, "model", "keyword", "policy_keyword_label.txt"),
            "oov_token": "[UNK]",
            "padding_token": "[PAD]"
        }
        model_config = {
            'embedding': {
                'token_embedders': {
                    'tokens': {'num_embeddings': 21128},
                    'segments': {'num_embeddings': 2},
                    'positions': {'num_embeddings': 512}
                },
                'embedding_dim': 768,
                'dropout': 0.1
            },
            "model_config": {
                # "vocab_size_or_config_json_file": 81216,
                "vocab_size": 21128,
                "hidden_size": 768,
                "num_attention_heads": 12,
                "intermediate_size": 3072,
                "hidden_act": "gelu",
                "hidden_dropout_prob": 0.1,
                "attention_probs_dropout_prob": 0.1,
                "max_position_embeddings": 512,
                "type_vocab_size": 2,
                "initializer_range": 0.02,
                'bert_encoder1': {
                    "num_hidden_layers": 11,
                },
                'bert_encoder2': {
                    "num_hidden_layers": 1,
                }
            },
            'dropout': 0.1,
        }
        DataLoadConfig = {
            "tokenizer": WhitespaceTokenizer(),
            "max_sequence_length": 100,
            "lazy": False
        }
        vocab = get_vocab_from_files(**vocab_config)
        reader = BertClassificationJsonReader.from_params(params=Params(DataLoadConfig))
        self.model = BertFreezeScorer.from_params(params=Params(deepcopy(model_config)), dataset_reader=reader, \
                                             model_path=os.path.join(current_path, "model", "keyword", "bert_best.th"), sentence_size=100,
                                             vocab=vocab)
        self.bert_token = BertTokenizer(vocab_config["vocab_file"])

    def predict(self, sentence):
        sentence = " ".join(self.bert_token.tokenize(sentence))
        results = self.model.predict(sentence)
        return results

    def predicts(self, sentences):
        sentences = [" ".join(self.bert_token.tokenize(sentence)) for sentence in sentences]
        results = self.model.predict_batch(sentences)
        return results



