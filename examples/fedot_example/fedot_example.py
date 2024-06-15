from repo_copilot.rag.rag import RAGApp


class FedotDataSet:
    def __init__(self):
        self.links = ["https://fedot.readthedocs.io/en/latest/introduction/what_is_fedot.html",
                      "https://fedot.readthedocs.io/en/latest/introduction/fedot_features/main_features.html",
                      "https://fedot.readthedocs.io/en/latest/introduction/tutorial/environment_setup/manual_installation.html",
                      "https://fedot.readthedocs.io/en/latest/examples/classification_example.html",
                      "https://fedot.readthedocs.io/en/latest/examples/ts_forecasting.html",
                      "https://fedot.readthedocs.io/en/latest/examples/regression_example.html",
                      "https://fedot.readthedocs.io/en/latest/examples/ts_forecasting.html",
                      "https://fedot.readthedocs.io/en/latest/examples/data.html",
                      "https://fedot.readthedocs.io/en/latest/basics/pipeline_save_load.html",
                      "https://fedot.readthedocs.io/en/latest/api/api.html",
                      "https://fedot.readthedocs.io/en/latest/faq/abstract.html",
                      "https://fedot.readthedocs.io/en/latest/faq/features.html",
                      "https://fedot.readthedocs.io/en/latest/faq/api_usage.html",
                      "https://fedot.readthedocs.io/en/latest/basics/main_concepts.html",
                      "https://fedot.readthedocs.io/en/latest/basics/tabular_data.html",
                      "https://fedot.readthedocs.io/en/latest/basics/ts_forecasting.html",
                      "https://fedot.readthedocs.io/en/latest/basics/multi_modal_tasks.html",
                      "https://fedot.readthedocs.io/en/latest/basics/pipeline_save_load.html",
                      "https://fedot.readthedocs.io/en/latest/advanced/hyperparameters_tuning.html",
                      "https://fedot.readthedocs.io/en/latest/advanced/data_preprocessing.html",
                      "https://fedot.readthedocs.io/en/latest/advanced/pipeline_import_export.html",
                      "https://fedot.readthedocs.io/en/latest/advanced/atomized_model.html",
                      "https://fedot.readthedocs.io/en/latest/api/data.html",
                      "https://fedot.readthedocs.io/en/latest/api/api.html",
                      "https://fedot.readthedocs.io/en/latest/api/node.html",
                      "https://fedot.readthedocs.io/en/latest/api/repository.html",
                      "https://fedot.readthedocs.io/en/latest/api/transformations.html"
                      ]


rag_app = RAGApp('deepseek-chat', repo_description='Fedot automl framework')

for link in FedotDataSet().links:
    rag_app.add(link)
