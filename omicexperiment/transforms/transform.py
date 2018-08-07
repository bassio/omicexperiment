

class ProxiedTransformMixin(object):
    def __get__(self, instance, owner):
        if isinstance(instance, TransformObjectsProxy):
            self.experiment = instance.experiment
            return self
        else:
            return super().__get__(instance, owner)

    
class TransformObjectsProxy(object):
    def __init__(self, experiment=None):
        self.experiment = experiment

    def __get__(self, instance, owner):
        #print("getting TransformObjectsProxy")
        self.experiment = instance
        return self
    
    
class Transform(object):
    def __dapply__(self, experiment):
        return NotImplementedError

    def __eapply__(self, experiment):
        return NotImplementedError
    
    def __get__(self, instance, owner):
        if isinstance(instance, TransformObjectsProxy):
            #print("instance is a TransformObjectsProxy")
            return self.__eapply__(instance.experiment) #experiment attribute of the TranformObjectsProxy
            
        return instance.__dict__[self.name]
    
    def __set__(self, instance, value):
        instance.__dict__[self.name] = value
    
    def __set_name__(self, owner, name):
        self.name = name


class Filter(Transform):
    def __init__(self, operator=None, value=None):
        self.operator = operator
        self.value = value
    
    def __get__(self, instance, owner):
        return self
    
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

    def __repr__(self):
        base_repr = object.__repr__(self)[1:-1]
        full_repr = "<{} - operator:{}; value:{};>".format(base_repr, str(self.operator), str(self.value))
        return full_repr


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

    def __repr__(self):
        base_repr = object.__repr__(self)[1:-1]
        full_repr = "<{} - attribute:{}; operator:{}; value:{};>".format(base_repr, str(self.attribute), str(self.operator), str(self.value))
        return full_repr


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
