package edu.sjtu.zhusy54.qrcode;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.Toast;

import com.google.zxing.BarcodeFormat;
import com.google.zxing.MultiFormatWriter;
import com.google.zxing.WriterException;
import com.google.zxing.common.BitMatrix;

/**
 * Created by Syman-Z on 2016/2/25.
 */
public class TestEncoder extends Activity {
    EditText textContent;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.encoder);

        textContent = (EditText)findViewById(R.id.gen_content);
        Button genBtn = (Button)findViewById(R.id.btn_generate);
        genBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                try {
                    String contentString = textContent.getText().toString();
                    if (!contentString.equals("")) {
                        BitMatrix matrix = new MultiFormatWriter().encode(contentString,
                                BarcodeFormat.QR_CODE, 300, 300);
                        int width = matrix.getWidth();
                        int height = matrix.getHeight();
                        int[] pixels = new int[width * height];

                        for (int y = 0; y < height; y++) {
                            for (int x = 0; x < width; x++) {
                                if (matrix.get(x, y)) {
                                    pixels[y * width + x] = Color.BLACK;
                                }
                            }
                        }
                        Bitmap bitmap = Bitmap.createBitmap(width, height,
                                Bitmap.Config.ARGB_8888);
                        bitmap.setPixels(pixels, 0, width, 0, 0, width, height);
                        ImageView image1 = new ImageView(TestEncoder.this);
                        image1.setImageBitmap(bitmap);
                        new AlertDialog.Builder(TestEncoder.this)
                                .setTitle("QR Code")
                                .setIcon(android.R.drawable.ic_dialog_info)
                                .setView(image1)
                                .setPositiveButton("Confirm", new DialogInterface.OnClickListener(){
                                    @Override
                                    public void onClick(DialogInterface dialog, int which) {
                                        dialog.dismiss();
                                    }
                                })
                                .show();
//                        Bitmap qrCodeBitmap = EncodingHandler.createQRCode(contentString, 350);
//                        qrImgImageView.setImageBitmap(qrCodeBitmap);
                    }else {
                        Toast.makeText(TestEncoder.this, "Text can not be empty", Toast.LENGTH_SHORT).show();
                    }

                } catch (WriterException e) {
                    // TODO Auto-generated catch block
                    e.printStackTrace();
                }
            }
        });
    }
}
