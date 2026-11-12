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
        Button btnTestQuiz = findViewById(R.id.btn_test_quiz);
        Button btnTestRest = findViewById(R.id.btn_test_rest);

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

        // 测试功能 1：立即进入答题界面
        btnTestQuiz.setOnClickListener(v -> {
            Prefs.setState(this, Prefs.STATE_QUIZ);
            Intent intent = new Intent(this, LockActivity.class);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(intent);
        });

        // 测试功能 2：设置休息 10 秒，走完自动转入答题
        btnTestRest.setOnClickListener(v -> {
            Prefs.setState(this, Prefs.STATE_RESTING);
            Prefs.setRestSeconds(this, 10);
            Intent intent = new Intent(this, LockActivity.class);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(intent);
        });
    }
}
