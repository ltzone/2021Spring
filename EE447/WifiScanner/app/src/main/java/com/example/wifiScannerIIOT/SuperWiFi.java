package com.example.wifiScannerIIOT;


/*****************************************************************************************************************
 * Created by HelloShine on 2019-3-24.
 * ***************************************************************************************************************/
import java.io.File;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.sql.Date;
import java.text.SimpleDateFormat;
import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import android.content.Context;
import android.net.wifi.ScanResult;
import android.net.wifi.WifiManager;
import android.os.Environment;
import android.util.Log; //Log can be utilized for debug.
import android.util.Pair;
import android.widget.TextView;

public class SuperWiFi extends MainActivity{

    /*****************************************************************************************************************
     * When you run the APP in your mobile phone, you can utilize the following code for debug:
     * Log.d("TEST_INFO","Your Own String Type Content Here");
     * You can also generate the String via ("String" + int/double value). for example, "CurTime " + 20 = "CurTime 20"
     * ***************************************************************************************************************/
    private String FileLabelName = "ZLT";// Define the file Name
    /*****************************************************************************************************************
     * You can define the Wi-Fi SSID to be measured in FileNameGroup, more than 2 SSIDs are OK.
     * It is noting that multiple Wi-Fi APs might share the same SSID such as SJTU.
     * ***************************************************************************************************************/
    private String FileNameGroup[];// = {"SJTU","AndroidWifi"};

    private int TestTime = 10;//Number of measurement
    private int ScanningTime = 1000;//Wait for (?) ms for next scan

    private int NumberOfWiFi = 1;// = FileNameGroup.length;

    // RSS_Value_Record and RSS_Measurement_Number_Record are used to record RSSI values
    private int[] RSS_Value_Record = new int[NumberOfWiFi];
    private int[] RSS_Measurement_Number_Record = new int[NumberOfWiFi];
    private Pair<Double,Double> locRes;


    private WifiManager mWiFiManager = null;
    private Vector<String> scanned = null;
    boolean isScanning = false;
    private Context context = null;
    private Map<String,Pair<Double,Double>> refLocs = null;

    public SuperWiFi(Context context, TextView ipText, TextView locText)
    {
        this.mWiFiManager = (WifiManager)context.getSystemService(Context.WIFI_SERVICE);
        this.context = context;
        this.scanned = new Vector<String>();
        this.FileNameGroup = ipText.getText().toString().split(",");
        this.NumberOfWiFi = FileNameGroup.length;
        this.RSS_Value_Record = new int[NumberOfWiFi];
        this.RSS_Measurement_Number_Record = new int[NumberOfWiFi];
        String[] locs = locText.getText().toString().split(";");
        this.refLocs = IntStream.range(0, FileNameGroup.length)
                .mapToObj(i -> {
                    String[] seq = locs[i].split(",");
                    Double d1 = Double.parseDouble(seq[0]);
                    Double d2 = Double.parseDouble(seq[1]);
                    Pair<Double,Double> loc = new Pair<>(d1,d2);
                    return new Pair<>(FileNameGroup[i], loc);
                })
                .collect(Collectors.toMap(v -> v.first, v -> v.second));
    }

    private double computeDist(double RSSI){
//         d=10^((ABS(RSSI)-A)/(10*n))
        double A = -40, n = 4;
        return Math.pow(10, (Math.abs(RSSI) - A)/10/n);
    }

    private void startScan()//The start of scanning
    {
        this.isScanning = true;
        Thread scanThread = new Thread(new Runnable()
        {
            public void run() {
                scanned.clear();//Clear last result
                for(int index = 1;index <= NumberOfWiFi; index++){
                    RSS_Value_Record[index - 1] = 0;
                    RSS_Measurement_Number_Record[index - 1] = 1;
                }
                int CurTestTime = 1; //Record the test time and write into the SD card
                SimpleDateFormat formatter = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
                Date curDate = new Date(System.currentTimeMillis()); //Get the current time
                String CurTimeString = formatter.format(curDate);
                for(int index = 1;index <= NumberOfWiFi; index++){
                    write2file(FileLabelName + "-" + FileNameGroup[index - 1] + ".txt","Test_ID: " + testID + " TestTime: " + CurTimeString + " BEGIN\r\n");
                }
                //Scan for a certain times
                while(CurTestTime++ <= TestTime) performScan();

                for(int index = 1;index <= NumberOfWiFi; index++){//Record the average of the result
                    scanned.add(FileLabelName + "-" + FileNameGroup[index - 1] + " = " + RSS_Value_Record[index - 1]/ RSS_Measurement_Number_Record[index - 1] + "\r\n");
                }
                write2file("temp.txt", scanned.toString());
                Log.d("TEST_INFO","-----------------------");
                Log.d("TEST_INFO",scanned.toString());
                Log.d("TEST_INFO","-----------------------");

                /*****************************************************************************************************************

                 You can insert your own code here for localization.

                 Solve:
                 2x(x1-x3)+2y(y1-y3)=d3^2-d_1^2+y_1^2-y_3^2+x_1^2-x_3^2
                 2x(x2-x3)+2y(y2-y3)=d3^2-d_2^2+y_2^2-y_3^2+x_2^2-x_3^2

                 d=10^((ABS(RSSI)-A)/(10*n))

                 * ***************************************************************************************************************/
                if (NumberOfWiFi == 3){
                    double d1 = computeDist(RSS_Value_Record[0]/RSS_Measurement_Number_Record[0]);
                    double d2 = computeDist(RSS_Value_Record[1]/RSS_Measurement_Number_Record[1]);
                    double d3 = computeDist(RSS_Value_Record[2]/RSS_Measurement_Number_Record[2]);
                    Log.d("TEST-INFO", String.format("%f%f%f", d1, d2, d3));
                    Pair<Double,Double> loc1 = refLocs.getOrDefault(FileNameGroup[0], new Pair<>(0., 0.));
                    Pair<Double,Double> loc2 = refLocs.getOrDefault(FileNameGroup[1], new Pair<>(0., 0.));
                    Pair<Double,Double> loc3 = refLocs.getOrDefault(FileNameGroup[2], new Pair<>(0., 0.));
                    double x1 = loc1.first, y1 = loc1.second, x2 = loc2.first, y2 = loc2.second,
                            x3 = loc3.first, y3 = loc3.second;
                    double[] coef1 = {2*(x1-x3), 2*(y1-y3), d3*d3-d1*d1+y1*y1-y3*y3+x1*x1-x3*x3 };
                    double[] coef2 = {2*(x2-x3), 2*(y2-y3), d3*d3-d2*d2+y2*y2-y3*y3+x2*x2-x3*x3 };
                    locRes = new EqnSolver(coef1, coef2).solve();
                }


                for(int index = 1;index <= NumberOfWiFi; index++){//Mark the end of the test in the file
                    write2file(FileLabelName + "-" + FileNameGroup[index - 1] + ".txt","testID:"+testID+"END\r\n");
                }
                isScanning=false;
            }
        });
        scanThread.start();
    }

    public String getLocRes(){
        if (locRes != null) {
            return "Your Location: " + locRes.first.toString() + "," + locRes.second.toString() +"\n";
        } else {
            return "";
        }
    }

    private void performScan()//The realization of the test
    {
        if(mWiFiManager == null)
            return;
        try
        {
            if(!mWiFiManager.isWifiEnabled())
            {
                mWiFiManager.setWifiEnabled(true);
            }
            mWiFiManager.startScan();//Start to scan
            try {
                Thread.sleep(ScanningTime);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            this.scanned.clear();
            List<ScanResult> sr = mWiFiManager.getScanResults();
            Iterator<ScanResult> it = sr.iterator();
            while(it.hasNext())
            {
                ScanResult ap = it.next();
                for(int index = 1;index <= FileNameGroup.length; index++){
                    if (ap.SSID.equals(FileNameGroup[index - 1])){//Write the result to the file
                        RSS_Value_Record[index-1] = RSS_Value_Record[index-1] + ap.level;
                        RSS_Measurement_Number_Record[index - 1]++;
                        write2file(FileLabelName + "-" + FileNameGroup[index - 1] + ".txt",ap.level+"\r\n");
                    }
                }
            }
        }
        catch (Exception e)
        {
            this.isScanning = false;
            this.scanned.clear();
        }
    }




    public void ScanRss(){
        Log.d("TEST_INFO", "Hello from ScanRSS");
        startScan();
    }
    public boolean isscan(){
        return isScanning;
    }
    public Vector<String> getRSSlist(){
        return scanned;
    }

    private void write2file(String filename, String a){//Write to the SD card
        try {
            Log.d("TEST_INFO",context.getExternalCacheDir().getPath());
            File file = new File(context.getExternalCacheDir().getPath()+"/"+filename);
            if (!file.exists()){
                file.createNewFile();} // Open a random filestream by Read&Write
            RandomAccessFile randomFile = new
                    RandomAccessFile(context.getExternalCacheDir().getPath() +"/"+filename, "rw"); // The length of the file(byte)
            long fileLength = randomFile.length(); // Put the writebyte to the end of the file
            randomFile.seek(fileLength);
            randomFile.writeBytes(a);
            randomFile.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}