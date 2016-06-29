 

class TSS(Transform):
    @staticmethod
    def apply_transform(experiment):
        rel_counts = experiment.data_df.apply(lambda c: c / c.sum() * 100, axis=0)
        return experiment.with_data_df(rel_counts)
    
