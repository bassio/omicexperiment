from omicexperiment.transforms.transform import Transform


class TSS(Transform):
    @classmethod
    def __dapply__(cls, experiment):
        rel_counts = experiment.data_df.apply(lambda c: c / c.sum() * 100, axis=0)
        return rel_counts

    @classmethod
    def __eapply__(cls, experiment):
        rel_counts = cls.__dapply__(experiment)
        return experiment.with_data_df(rel_counts)
