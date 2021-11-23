from sklearn.mixture import GaussianMixture
from sklearn.cluster import DBSCAN
import numpy as np
import warnings
warnings.filterwarnings("ignore")

class Cluster:

    def __init__(self):
        self.gausemixture = None
        self.gauseparameters = None
        self.dbcan = None
        self.dbcan_normal_datas_ = []
        self.mean = 0
        self.covariances = 0
        self.limit_hight = 0
        self.limit_low = 0
        self.limit_hightest = 0
        self.limit_lowest = 0
        self.normal_high = 0
        self.normal_low = 0

    def initialize(self):
        self.gausemixture = None
        self.gauseparameters = None
        self.dbcan = None
        self.dbcan_normal_datas_ = []
        self.mean = 0
        self.covariances = 0
        self.limit_hight = 0
        self.limit_low = 0
        self.limit_hightest = 0
        self.limit_lowest = 0
        self.normal_high = 0
        self.normal_low = 0

    def gausecluster(self, n_components, x):
        self.initialize()
        if x.shape == (-1, 1):
            self.gausemixture = GaussianMixture(n_components=n_components)
            self.gauseparameters = self.gausemixture.fit(X=x)
            mean_list = self.gauseparameters.means_
            cov_list = self.gauseparameters.covariances_
            weights_list = self.gauseparameters.weights_
            mean_list = np.ravel(mean_list)
            cov_list = np.ravel(cov_list)
            weights_list = np.ravel(weights_list)
            self.mean = sum(mean_list*weights_list)
            self.covariances = sum(cov_list*weights_list)
            self.limit_hightest = self.mean+1.96*self.covariances
            self.limit_lowest = self.mean - 1.96*self.covariances
            self.limit_hight = self.mean + 1.58*self.covariances
            self.limit_low = self.mean - 1.58*self.covariances
        else:
            x = x.reshape(-1, 1)
            self.gausemixture = GaussianMixture(n_components=n_components)
            self.gauseparameters = self.gausemixture.fit(X=x)
            mean_list = self.gauseparameters.means_
            cov_list = self.gauseparameters.covariances_
            weights_list = self.gauseparameters.weights_
            mean_list = np.ravel(mean_list)
            cov_list = np.ravel(cov_list)
            weights_list = np.ravel(weights_list)
            self.mean = sum(mean_list * weights_list)
            self.covariances = sum(cov_list * weights_list)
            self.limit_hightest = self.mean + 1.96 * self.covariances
            self.limit_lowest = self.mean - 1.96 * self.covariances
            self.limit_hight = self.mean + 1.58 * self.covariances
            self.limit_low = self.mean - 1.58 * self.covariances

        return self.limit_hight, self.limit_low, self.limit_hightest, self.limit_lowest

    def dbscancluster(self, eps, min_samples, x, interval_1, interval_2):
        self.initialize()
        if x.shape == (-1, 1):
            self.dbcan = DBSCAN(eps, min_samples).fit(x)
            index_normal = np.where(self.dbcan.labels_ == 0)
            self.dbcan_normal_datas_ = []
            for i in index_normal[0].ravel():
                self.dbcan_normal_datas_.append(x[i])
            self.mean = np.mean(self.dbcan_normal_datas_)
            self.normal_high = np.max(self.dbcan_normal_datas_)
            self.normal_low = np.min(self.dbcan_normal_datas_)
            if self.normal_high < 0 and self.normal_low < 0:
                self.limit_hight = - (abs(self.normal_high) * (1 - interval_1))
                self.limit_low = -(abs(self.normal_low) * (1 + interval_1))
                self.limit_hightest = - (abs(self.limit_hight) * (1 - interval_2))
                self.limit_lowest = -(abs(self.limit_low) * (1 + interval_2))

            elif self.normal_low < 0 and self.normal_high > 0:
                self.limit_hight = self.normal_high * (1 + interval_1)
                self.limit_low = self.limit_low = -(abs(self.normal_low) * (1 - interval_1))
                self.limit_hightest = self.limit_hight * (1 + interval_2)
                self.limit_lowest = -(abs(self.limit_low) * (1 - interval_2))

            else:
                self.limit_hight = self.normal_high * (1 + interval_1)
                self.limit_low = self.normal_low * (1 - interval_1)
                self.limit_hightest = self.limit_hight * (1 + interval_2)
                self.limit_lowest = self.limit_low * (1 - interval_2)

        else:
            x = x.reshape(-1, 1)
            self.dbcan = DBSCAN(eps, min_samples).fit(x)
            index_normal = np.where(self.dbcan.labels_ == 0)
            self.dbcan_normal_datas_ = []
            for i in index_normal[0].ravel():
                self.dbcan_normal_datas_.append(x[i])
            self.mean = np.mean(self.dbcan_normal_datas_)
            self.normal_high = np.max(self.dbcan_normal_datas_)
            self.normal_low = np.min(self.dbcan_normal_datas_)
            if self.normal_high < 0 and self.normal_low < 0:
                self.limit_hight = - (abs(self.normal_high) * (1 - interval_1))
                self.limit_low = -(abs(self.normal_low) * (1 + interval_1))
                self.limit_hightest = - (abs(self.limit_hight) * (1 - interval_2))
                self.limit_lowest = -(abs(self.limit_low) * (1 + interval_2))

            elif self.normal_low < 0 and self.normal_high > 0:
                self.limit_hight = self.normal_high * (1 + interval_1)
                self.limit_low = self.limit_low = -(abs(self.normal_low) * (1 - interval_1))
                self.limit_hightest = self.limit_hight * (1 + interval_2)
                self.limit_lowest = -(abs(self.limit_low) * (1 + interval_2))

            else:
                self.limit_hight = self.normal_high * (1 + interval_1)
                self.limit_low = self.normal_low * (1 - interval_1)
                self.limit_hightest = self.limit_hight * (1 + interval_2)
                self.limit_lowest = self.limit_low * (1 - interval_2)

        return self.mean, self.normal_high, self.normal_low, self.limit_hight, self.limit_low, self.limit_hightest\
            , self.limit_lowest


class LoadRelated(Cluster):

    def __init__(self):
        super().__init__()
        self.correlation = 0
        self.fit_result = []

    def caculate_correlation(self, data, load):
        self.correlation = np.corrcoef(data, load)[1][0]

        return self.correlation

    def linear_fit(self, data, load, deg):
        self.fit_result = np.polyfit(data, load, deg=deg)

        return self.fit_result

