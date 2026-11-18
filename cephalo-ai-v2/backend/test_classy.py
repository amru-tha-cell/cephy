from app.analysis.classification import classify_skeletal_pattern

# print(classify_skeletal_pattern({"ANB": 2.0}))
# print(classify_skeletal_pattern({"ANB": 5.2}))
# print(classify_skeletal_pattern({"ANB": -2.0}))
# from app.analysis.jaw_assessment import assess_jaws

# print(assess_jaws({
#     "SNA": 82,
#     "SNB": 80,
#     "ANB": 2
# }))
# from app.analysis.classification import classify_skeletal_pattern
from app.analysis.jaw_assessment import assess_jaws
from app.analysis.surgery_assessment import assess_surgical_considerations

# measurements = {
#     "SNA": 85,
#     "SNB": 77,
#     "ANB": 8
# }

# classification = classify_skeletal_pattern(measurements)
# jaw_results = assess_jaws(measurements)

# result = assess_surgical_considerations(
#     classification,
#     jaw_results
# )

# print(result)
# measurements = {
#     "SNA": 82,
#     "SNB": 80,
#     "ANB": 2
# }

# classification = classify_skeletal_pattern(measurements)
# jaw_results = assess_jaws(measurements)

# print(
#     assess_surgical_considerations(
#         classification,
#         jaw_results
#     )
# )
from app.services.clinical_analysis import generate_clinical_analysis

# measurements = {
#     "SNA": 85,
#     "SNB": 77,
#     "ANB": 8
# }

# result = generate_clinical_analysis(measurements)

# print(result)
measurements = {
    "SNA": 82,
    "SNB": 80,
    "ANB": 2
}

print(generate_clinical_analysis(measurements))