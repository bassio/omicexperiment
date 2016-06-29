
class FilterExpression(object):
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
        
    def return_value(self, experiment_obj):
        return NotImplementedError
        
        
class AttributeFilter(FilterExpression):
    def __init__(self, operator=None, value=None, attribute=None):
        FilterExpression.__init__(self, operator, value)
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

class GroupByFilter(FilterExpression):
    def __init__(self, value=None):
        FilterExpression.__init__(self, operator='groupby', value=value)
    
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
