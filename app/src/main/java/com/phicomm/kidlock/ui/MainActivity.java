package com.phicomm.kidlock.ui;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;

import com.phicomm.kidlock.R;
import com.phicomm.kidlock.core.TimeWallet;
import com.phicomm.kidlock.core.ZenConfig;
import com.phicomm.kidlock.service.WatchdogService;
import com.phicomm.kidlock.util.Prefs;
import com.phicomm.kidlock.util.RootUtils;

public class MainActivity extends AppCompatActivity {

    private TextView tvBalance;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        tvBalance = findViewById(R.id.tv_wallet_balance);
        TextView tvCurfew = findViewById(R.id.tv_curfew_info);
        Button btnEarnTime = findViewById(R.id.btn_earn_time);
        Button btnGrant = findViewById(R.id.btn_grant);
        Button btnTestRest = findViewById(R.id.btn_test_rest);

        ZenConfig.Model cfg = ZenConfig.get(this);
        tvCurfew.setText(String.format("🌙 夜间免打扰：每天 %s ~ %s (大人观影不受限)", 
                cfg.curfew.start_time, cfg.curfew.end_time));

        // 核心亮点：主动挑战赢取时间
        btnEarnTime.setOnClickListener(v -> {
            Prefs.setState(this, Prefs.STATE_QUIZ);
            Intent intent = new Intent(this, LockActivity.class);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(intent);
        });

        btnGrant.setOnClickListener(v -> {
            if (RootUtils.checkRoot()) {
                startService(new Intent(this, WatchdogService.class));
                Toast.makeText(this, "守护已激活！夜间自动休眠！", Toast.LENGTH_SHORT).show();
            } else {
                Toast.makeText(this, "请授予 Root 权限以启用系统级防护", Toast.LENGTH_LONG).show();
            }
        });

        btnTestRest.setOnClickListener(v -> {
            Prefs.setState(this, Prefs.STATE_RESTING);
            Prefs.setRestSeconds(this, 10);
            Intent intent = new Intent(this, LockActivity.class);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(intent);
        });
    }

    @Override
    protected void onResume() {
        super.onResume();
        tvBalance.setText("⚡ 剩余娱乐燃料：" + TimeWallet.getFormattedBalance(this));
    }
}
