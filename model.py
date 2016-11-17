from features.feature_params import FeatureParameters
from parsing import config
from parsing.action import Actions
from parsing.config import Config


class Model(object):
    def __init__(self, model_type, filename, labels=None, feature_extractor=None, model=None):
        self.model_type = model_type
        self.filename = filename
        if feature_extractor is not None and model is not None:
            self.feature_extractor = feature_extractor
            self.model = model
            return

        if model_type == config.SPARSE_PERCEPTRON:
            from features.sparse_features import SparseFeatureExtractor
            from linear.sparse_perceptron import SparsePerceptron
            self.feature_extractor = SparseFeatureExtractor()
            self.model = SparsePerceptron(filename, labels)
        elif model_type == config.DENSE_PERCEPTRON:
            from features.embedding import FeatureEmbedding
            from linear.dense_perceptron import DensePerceptron
            self.feature_extractor = self.dense_features_wrapper(FeatureEmbedding)
            self.model = DensePerceptron(filename, labels, num_features=self.feature_extractor.num_features())
        elif model_type == config.MLP_NN:
            from features.enumerator import FeatureEnumerator
            from nn.feedforward import MLP
            self.feature_extractor = self.dense_features_wrapper(FeatureEnumerator)
            self.model = MLP(filename, labels, input_params=self.feature_extractor.params)
        elif model_type == config.BILSTM_NN:
            from features.enumerator import FeatureEnumerator
            from features.indexer import FeatureIndexer
            from nn.bilstm import BiLSTM
            self.feature_extractor = FeatureIndexer(self.dense_features_wrapper(FeatureEnumerator))
            self.model = BiLSTM(filename, labels, input_params=self.feature_extractor.params)
        else:
            raise ValueError("Invalid model type: '%s'" % model_type)

    @staticmethod
    def dense_features_wrapper(wrapper):
        from features.dense_features import DenseFeatureExtractor
        params = [
            FeatureParameters("w", Config().args.wordvectors, Config().args.maxwords, Config().args.worddropout),
            FeatureParameters("t", Config().args.tagdim, Config().args.maxtags),
            FeatureParameters("e", Config().args.labeldim, Config().args.maxedgelabels),
            FeatureParameters("p", Config().args.punctdim, Config().args.maxpuncts),
            FeatureParameters("x", Config().args.gapdim, Config().args.maxgaps),
            FeatureParameters("A", Config().args.actiondim, Config().args.maxactions),
        ]
        return wrapper(DenseFeatureExtractor(), params)

    def init_features(self, state, train):
        self.model.init_features(self.feature_extractor.init_features(state), train)

    def finalize(self, finished_epoch):
        return Model(model_type=self.model_type,
                     filename=self.filename,
                     feature_extractor=self.feature_extractor.finalize(),
                     model=self.model.finalize(finished_epoch))

    def save(self):
        if self.filename is not None:
            try:
                self.feature_extractor.save(self.filename)
                self.model.save()
            except Exception as e:
                raise IOError("Failed saving model to '%s'" % self.filename, e)

    def load(self):
        if self.filename is not None:
            try:
                self.feature_extractor.load(self.filename)
                self.model.load()
                Actions().all = self.model.labels
            except Exception as e:
                raise IOError("Failed loading model from '%s'" % self.filename, e)
