
class Transform(object):
    def apply_transform(self, experiment):
        return NotImplementedError
    
    def __dapply__(self, experiment):
        return NotImplementedError
        
    def __eapply__(self, experiment):
        return NotImplementedError


class Filter(Transform):
    def __init__(self, operator=None, value=None):
        self.operator = operator
        self.value = value
        
    def __lt__(self, other):
        return self.__class__('__lt__', other)
        
    def __le__(self, other):
        return self.__class__('__le__', other)
        
    def __eq__(self, other):
        return self.__class__('__eq__', other)
        
    def __ne__(self, other):
        return self.__class__('__ne__', other)
        
        
    def __gt__(self, other):
        return self.__class__('__gt__', other)
        
    def __ge__(self, other):
        return self.__class__('__ge__', other)
        
    def __dapply__(self, experiment_obj):
        return NotImplementedError

    def __eapply__(self, experiment):
        filtered_df = self.__class__.__dapply__(self, experiment)
        return experiment.with_data_df(filtered_df)
        
        
class AttributeFilter(Filter):
    def __init__(self, operator=None, value=None, attribute=None):
        Filter.__init__(self, operator, value)
        self.attribute = attribute
    
    def new(self, operator=None, value=None, attribute=None):
        return self.__class__(operator,value, attribute)

    def __lt__(self, other):
        return self.__class__('__lt__', other, self.attribute)
        
    def __le__(self, other):
        return self.__class__('__le__', other, self.attribute)
        
    def __eq__(self, other):
        return self.__class__('__eq__', other, self.attribute)
        
    def __ne__(self, other):
        return self.__class__('__ne__', other, self.attribute)
        
    def __gt__(self, other):
        return self.__class__('__gt__', other, self.attribute)
        
    def __ge__(self, other):
        return self.__class__('__ge__', other, self.attribute)
    
    def __getattr__(self, name):
        return self.__class__(operator = self.operator, value=self.value, attribute=name)

    def __getitem__(self, item):
        return self.__class__(operator = self.operator, value=self.value, attribute=item)


class GroupByTransform(Transform):
    def __init__(self, value=None):
        Transform.__init__(self)
        self.value = value
    
    def __call__(self, value):
        return self.__class__(value)
    
    def __getitem__(self, value):
        return self.__class__(value)
    

class FlexibleOperatorMixin(object):
    def _op_function(self, dataframe):
        return getattr(dataframe, self.operator)

class AttributeFlexibleOperatorMixin(object):
    def _op_function(self, dataframe):
        return getattr(dataframe[self.attribute], self.operator)
