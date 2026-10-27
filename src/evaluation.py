
def calculate_precision(tp, fp):
    total_predictions = tp + fp

    if total_predictions == 0:
        return 0.0

    precision = tp / total_predictions

    return precision



def calculate_recall(tp, fn):
    total_actual_positives = tp + fn

    if total_actual_positives == 0:
        return 0.0

    recall = tp / total_actual_positives

    return recall



def calculate_f1_score(tp, fp, fn):
    precision = calculate_precision(tp, fp)
    recall = calculate_recall(tp, fn)

    if precision + recall == 0:
        return 0.0

    f1_score = 2 * (precision * recall) / (precision + recall)

    return f1_score

if __name__ == "__main__":
    print(calculate_precision(18,6))
    print(calculate_recall(32,8))
    print(calculate_f1_score(18,6,12))