package com.example.wifiScannerIIOT;

import android.util.Pair;

public class EqnSolver {
    private double coef1[]; // ax + by = c {a;b;c}
    private double coef2[]; // ax + by = c {a;b;c}

    EqnSolver(double[] coef1, double[] coef2){
        this.coef1 = coef1;
        this.coef2 = coef2;
    }

    Pair<Double, Double> solve(){
        Double x = (coef1[1]*coef2[2]-coef2[1]*coef1[2])/(coef1[1]*coef2[0]-coef2[1]*coef1[0]);
        Double y = (coef1[0]*coef2[2]-coef2[0]*coef1[2])/(coef1[0]*coef2[1]-coef2[0]*coef1[1]);

        return new Pair<>(x,y);
    }
}
