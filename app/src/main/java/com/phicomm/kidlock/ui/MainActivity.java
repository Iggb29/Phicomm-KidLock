package com.phicomm.kidlock.ui;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;

import com.phicomm.kidlock.R;
import com.phicomm.kidlock.service.WatchdogService;
import com.phicomm.kidlock.util.Prefs;
import com.phicomm.kidlock.util.RootUtils;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        TextView tvStatus = findViewById(R.id.tv_status);
        Button btnGrant = findViewById(R.id.btn_grant);

        btnGrant.setOnClickListener(v -> {
            boolean hasRoot = RootUtils.checkRoot();
            if (hasRoot) {
                tvStatus.setText("状态：已获取 Root 权限，守护中！");
                Toast.makeText(this, "Root 授权成功，守护已激活！", Toast.LENGTH_SHORT).show();
                startService(new Intent(this, WatchdogService.class));
            } else {
                tvStatus.setText("状态：未获得 Root 权限，请在弹窗中允许！");
            }
        });
    }
}
