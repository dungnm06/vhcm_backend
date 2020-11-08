import argparse
from classifiers.intent_classifier import train_intent_classifier
from classifiers.question_classifier import train_question_classifier

if __name__ == '__main__':
    # Load parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--type', type=int, help='Training type (Intent: 1, Question: 2)', required=True)
    parser.add_argument('-d', '--data', help='Train data file path', required=True)
    parser.add_argument('-o', '--output', help='Output path', default='/trained')
    parser.add_argument('-sl', '--sentencelength', type=int, help='Sentence max length', default=30)
    parser.add_argument('-b', '--batch', type=int, help='Training batch size', default=32)
    parser.add_argument('-e', '--epoch', type=int, help='Number of epochs', default=5)
    parser.add_argument('-lr', '--learningrate', type=float, help='Learning rate', default=2e-5)
    parser.add_argument('-eps', '--epsilon', type=float, help='Epsilon', default=1e-8)
    parser.add_argument('-a', '--activation', help='Activation function')
    args = parser.parse_args()

    type = args.type
    data = args.data
    output = args.output
    sentence_length = args.sentencelength
    batch = args.batch
    epoch = args.epoch
    learning_rate = args.learningrate
    epsilon = args.epsilon
    activation = args.activation

    if args.type == 1:
        if activation is None:
            activation = 'softmax'
        train_intent_classifier(data, output, sentence_length, batch, epoch, learning_rate, epsilon, activation)
    if args.type == 2:
        if activation is None:
            activation = 'sigmoid'
        train_question_classifier(data, output, sentence_length, batch, epoch, learning_rate, epsilon, activation)
