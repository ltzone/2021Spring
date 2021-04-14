package com.example.wifiScannerIIOT;

import android.content.Context;
import android.os.Bundle;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import android.view.View;

import android.view.Menu;
import android.view.MenuItem;

import android.Manifest;
import android.content.pm.PackageManager;

import java.util.Vector;

import android.app.Activity;
import android.widget.Button;
import android.widget.EditText;

import android.util.Log; //Log can be utilized for debug.
public class MainActivity extends AppCompatActivity {

    private SuperWiFi rss_scan =null;
    Vector<String> RSSList = null;
    private String testlist=null;
    public static int testID = 0;//The ID of the test result

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        final EditText wifiName = findViewById(R.id.wifiName);
        final TextView ipText = (TextView)findViewById(R.id.ipText);//The textlist of the average of the result
        final Button changactivity = (Button)findViewById(R.id.button1);//The start button
        final Button cleanlist = (Button)findViewById(R.id.button2);//Clear the textlist
        verifyStoragePermissions(this);
        final Context that = this;
        testlist="";
        testID=0;
        Log.d("TEST_INFO","INITIAL");
        changactivity.setOnClickListener(new Button.OnClickListener(){
            public void onClick(View v) {
                rss_scan=new SuperWiFi(that, wifiName);
                testID = testID + 1;
                rss_scan.ScanRss();
                while(rss_scan.isscan()){//Wait for the end
                }
                RSSList=rss_scan.getRSSlist();//Get the test result
                final TextView ipText = (TextView)findViewById(R.id.ipText);
                testlist=testlist+"testID:"+testID+"\n"+RSSList.toString()+"\n";
                ipText.setText(testlist);//Display the result in the textlist
            }
        });
        cleanlist.setOnClickListener(new Button.OnClickListener(){
            public void onClick(View v) {
                testlist="";
                ipText.setText(testlist);//Clear the textlist
                testID=0;
            }
        });
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }

    private static final int REQUEST_EXTERNAL_STORAGE = 1;
    private static final String[] PERMISSIONS_STORAGE = {
            Manifest.permission.READ_EXTERNAL_STORAGE,
            Manifest.permission.WRITE_EXTERNAL_STORAGE,
            Manifest.permission.ACCESS_NETWORK_STATE,
            Manifest.permission.CHANGE_WIFI_STATE,
            Manifest.permission.ACCESS_WIFI_STATE,
            Manifest.permission.CHANGE_WIFI_MULTICAST_STATE,
            Manifest.permission.INTERNET,
            Manifest.permission.ACCESS_FINE_LOCATION };

    /**
     * Checks if the app has permission to write to device storage
     * If the app does not has permission then the user will be prompted to
     * grant permissions
     */
    public static void verifyStoragePermissions(Activity activity) {
        // Check if we have write permission
        int permission = ActivityCompat.checkSelfPermission(activity,
                Manifest.permission.WRITE_EXTERNAL_STORAGE);

        if (permission != PackageManager.PERMISSION_GRANTED) {
        // We don't have permission so prompt the user
            ActivityCompat.requestPermissions(activity, PERMISSIONS_STORAGE,
                    REQUEST_EXTERNAL_STORAGE);
        }
    }
}