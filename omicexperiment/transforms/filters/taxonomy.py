import pandas as pd
from omicexperiment.transforms.transform import Filter, AttributeFilter, AttributeFlexibleOperatorMixin


class TaxonomyAttributeFilter(AttributeFilter, AttributeFlexibleOperatorMixin):
    def __dapply__(self, experiment):
        _op = self._op_function(experiment._counts_with_tax())
        criteria = _op(self.value)
        return experiment.data_df[criteria]
    
    def __eapply__(self, experiment):
        filtered_df = self.__dapply__(experiment)
        return experiment.with_data_df(filtered_df)
        
