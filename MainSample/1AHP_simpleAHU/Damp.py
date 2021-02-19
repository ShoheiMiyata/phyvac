class Damper():
    def cal(self, g, damp,
            coef=[[1.0,-0.00001944,0.018,0.18,-0.007], [0.8,0.0000864,0.036,0.132,0.0684],
                 [0.6,0.001296,0.072,0.384,0.1001], [0.4,0.00108,0.36,-0.582,0.0662], [0.2,-0.0216,4.32,-5.34,0.2527]]):
        # x     :ダンパ開度(0.0~1.0)
        # dp    :圧力損失[Pa]
        # g     :流量[m^3/min]
        # dp = a * g^3 + b * g^2 + c * g + d
        # coef = [[x1, a_x1, b_x1, c_x1, d_x1], ... , [xn, a_xn, b_xn, c_xn, d_xn]]  (x1 >x2 >...> xn)
        self.g = g
        self.damp = damp
        self.coef = coef
        n = len(self.coef)
        if self.damp >= self.coef[0][0]:
            self.dp = (self.coef[0][1] * self.g ** 3 + self.coef[0][2] * self.g ** 2 + self.coef[0][3] * self.g + self.coef[0][4])
        elif self.damp < self.coef[n-1][0]:
            self.dp = (self.coef[n-1][1] * self.g ** 3 + self.coef[n-1][2] * self.g ** 2 + self.coef[n-1][3] * self.g + self.coef[n-1][4])
        else:
            for i in range(1, n):    # 線形補間の上限・下限となる曲線を探す
                self.hl = self.coef[i-1]  # higher limit curve
                self.ll = self.coef[i]    # lower limit curve
                if self.ll[0] <= self.damp < self.hl[0]:
                    break
            dp_h = (self.hl[1] * self.g ** 3 + self.hl[2] * self.g ** 2 + self.hl[3] * self.g + self.hl[4])
            dp_l = (self.ll[1] * self.g ** 3 + self.ll[2] * self.g ** 2 + self.ll[3] * self.g + self.ll[4])
            self.dp = (dp_h - dp_l) / (self.hl[0]-self.ll[0]) * (self.damp - self.ll[0]) + dp_l
        return self.dp
        
