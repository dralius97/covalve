with open('./prompt/query_analyze_prompt.txt') as f:
    query_analisis_prompt = f.read()

with open('./prompt/clarification_template.txt') as f:
    main_llm_clarification_prompt = f.read()

with open('./prompt/main_llm_response.txt') as f:
    main_llm_response_prompt = f.read()

query_analisis_prompt = query_analisis_prompt
main_llm_clarification_prompt = main_llm_clarification_prompt
main_llm_response_prompt = main_llm_response_prompt