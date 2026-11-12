# -*- coding: utf-8 -*-
import os

files = {
    # 1. 全局动态配置文件
    "app/src/main/assets/config.json": """{
  "curfew": {
    "enabled": true,
    "start_time": "21:00",
    "end_time": "07:00"
  },
  "rules": {
    "default_watch_seconds": 1800,
    "default_rest_seconds": 600,
    "reward_seconds_per_quiz": 1800
  }
}
""",

    # 2. 升级字符串资源
    "app/src/main/res/values/strings.xml": """<resources>
    <string name="app_name">ZenScreen · 醒来</string>
</resources>
""",

    # 3. 核心配置解析引擎：ZenConfig.java
    "app/src/main/java/com/phicomm/kidlock/core/ZenConfig.java": """package com.phicomm.kidlock.core;

import android.content.Context;
import com.google.gson.Gson;
import com.google.gson.JsonObject;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class ZenConfig {
    public static class Model {
        public Curfew curfew = new Curfew();
        public Rules rules = new Rules();
    }
    public static class Curfew {
        public boolean enabled = true;
        public String start_time = "21:00";
        public String end_time = "07:00";
    }
    public static class Rules {
        public int default_watch_seconds = 1800; // 30 分钟
        public int default_rest_seconds = 600;   // 10 分钟
        public int reward_seconds_per_quiz = 1800;
    }

    private static Model cachedConfig = null;

    public static Model get(Context context) {
        if (cachedConfig != null) return cachedConfig;
        try {
            File ext = new File("/sdcard/zenscreen_config.json");
            InputStream is = ext.exists() ? new FileInputStream(ext) : context.getAssets().open("config.json");
            cachedConfig = new Gson().fromJson(new InputStreamReader(is, "UTF-8"), Model.class);
        } catch (Exception e) {
            cachedConfig = new Model();
        }
        return cachedConfig;
    }

    // 检查当前时间是否处于夜间免打扰时段
    public static boolean isNightCurfew(Context context) {
        Model cfg = get(context);
        if (!cfg.curfew.enabled) return false;
        try {
            SimpleDateFormat sdf = new SimpleDateFormat("HH:mm", Locale.getDefault());
            String nowStr = sdf.format(new Date());
            Date now = sdf.parse(nowStr);
            Date start = sdf.parse(cfg.curfew.start_time);
            Date end = sdf.parse(cfg.curfew.end_time);

            if (start.after(end)) { // 跨天时段，如 21:00 到 07:00
                return now.after(start) || now.before(end);
            } else {
                return now.after(start) && now.before(end);
            }
        } catch (Exception e) {
            return false;
        }
    }
}
""",

    # 4. 时间银行与记账内核：TimeWallet.java
    "app/src/main/java/com/phicomm/kidlock/core/TimeWallet.java": """package com.phicomm.kidlock.core;

import android.content.Context;
import com.phicomm.kidlock.util.Prefs;

public class TimeWallet {

    // 存入时间燃料（奖励）
    public static void deposit(Context context, int seconds) {
        int current = Prefs.getWatchSeconds(context);
        Prefs.setWatchSeconds(context, current + seconds);
        Prefs.setState(context, Prefs.STATE_NORMAL);
    }

    // 获取当前可用时间（格式化显示）
    public static String getFormattedBalance(Context context) {
        int sec = Prefs.getWatchSeconds(context);
        int mins = sec / 60;
        return mins + " 分钟";
    }
}
""",

    # 5. 抽象挑战引擎接口（解耦层）：IChallengeEngine.java
    "app/src/main/java/com/phicomm/kidlock/engine/IChallengeEngine.java": """package com.phicomm.kidlock.engine;

import android.content.Context;

public interface IChallengeEngine {
    String getTitle(); // 模块名称，例如：儿童思维挑战、银发八段锦、成人深思
    void onChallengePassed(Context context); // 挑战通过回调
}
""",

    # 6. 重构看门狗服务：融入时段免打扰与配置
    "app/src/main/java/com/phicomm/kidlock/service/WatchdogService.java": """package com.phicomm.kidlock.service;

import android.app.Service;
import android.content.Intent;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;

import com.phicomm.kidlock.core.ZenConfig;
import com.phicomm.kidlock.ui.LockActivity;
import com.phicomm.kidlock.util.Prefs;
import com.phicomm.kidlock.util.RootUtils;

public class WatchdogService extends Service {
    private Handler handler;
    private Runnable ticker;

    @Override
    public void onCreate() {
        super.onCreate();
        handler = new Handler(Looper.getMainLooper());
        ticker = new Runnable() {
            @Override
            public void run() {
                handleTick();
                handler.postDelayed(this, 1000);
            }
        };
        handler.post(ticker);
    }

    private void handleTick() {
        // 核心进化：夜间免打扰时段，看门狗彻底静默休眠，不打扰成年人看电影
        if (ZenConfig.isNightCurfew(this)) {
            return;
        }

        int state = Prefs.getState(this);
        if (state == Prefs.STATE_NORMAL) {
            int watchSec = Prefs.getWatchSeconds(this) - 1;
            if (watchSec <= 0) {
                Prefs.setState(this, Prefs.STATE_RESTING);
                Prefs.setRestSeconds(this, ZenConfig.get(this).rules.default_rest_seconds);
                launchLockActivity();
            } else {
                Prefs.setWatchSeconds(this, watchSec);
            }
        } else if (state == Prefs.STATE_RESTING) {
            int restSec = Prefs.getRestSeconds(this) - 1;
            if (restSec <= 0) {
                Prefs.setState(this, Prefs.STATE_QUIZ);
            } else {
                Prefs.setRestSeconds(this, restSec);
            }
            ensureLockForeground();
        } else if (state == Prefs.STATE_QUIZ) {
            ensureLockForeground();
        }
    }

    private void ensureLockForeground() {
        if (!LockActivity.isForeground) {
            launchLockActivity();
        }
    }

    private void launchLockActivity() {
        Intent intent = new Intent(this, LockActivity.class);
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        startActivity(intent);
        RootUtils.runCommand("am start -n com.phicomm.kidlock/.ui.LockActivity");
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        return START_STICKY;
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
""",

    # 7. 全新主界面仪表盘布局
    "app/src/main/res/layout/activity_main.xml": """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#0D1117"
    android:gravity="center"
    android:orientation="vertical"
    android:padding="30dp">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="ZenScreen · 醒来"
        android:textColor="#58A6FF"
        android:textSize="32sp"
        android:textStyle="bold" />

    <TextView
        android:id="@+id/tv_wallet_balance"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="15dp"
        android:text="⚡ 剩余娱乐燃料：计算中..."
        android:textColor="#FFD700"
        android:textSize="20sp" />

    <TextView
        android:id="@+id/tv_curfew_info"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="8dp"
        android:text="🌙 夜间免打扰时段：21:00 ~ 07:00 (自动休眠)"
        android:textColor="#8B949E"
        android:textSize="14sp" />

    <LinearLayout
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="35dp"
        android:orientation="horizontal">

        <!-- 范式转移：主动做题挑战以赢取时间 -->
        <Button
            android:id="@+id/btn_earn_time"
            android:layout_width="220dp"
            android:layout_height="65dp"
            android:layout_margin="10dp"
            android:background="@drawable/btn_tv_selector"
            android:focusable="true"
            android:text="💡 挑战工坊 (赚取30分钟)"
            android:textColor="#FFFFFF"
            android:textSize="16sp" />

        <Button
            android:id="@+id/btn_grant"
            android:layout_width="200dp"
            android:layout_height="65dp"
            android:layout_margin="10dp"
            android:background="@drawable/btn_tv_selector"
            android:focusable="true"
            android:text="🛡️ 激活/重启守护"
            android:textColor="#FFFFFF"
            android:textSize="16sp" />
    </LinearLayout>

    <!-- 测试专用通道 -->
    <LinearLayout
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="10dp"
        android:orientation="horizontal">

        <Button
            android:id="@+id/btn_test_rest"
            android:layout_width="160dp"
            android:layout_height="45dp"
            android:layout_margin="8dp"
            android:background="@drawable/btn_tv_selector"
            android:focusable="true"
            android:text="⏳ 测试：10秒休息"
            android:textColor="#81D4FA"
            android:textSize="14sp" />
    </LinearLayout>
</LinearLayout>
""",

    # 8. 全新主界面控制器：MainActivity.java
    "app/src/main/java/com/phicomm/kidlock/ui/MainActivity.java": """package com.phicomm.kidlock.ui;

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
"""
}

for path, content in files.items():
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("✨ ZenScreen V2.0 模块化代码已全自动重构就绪！")
