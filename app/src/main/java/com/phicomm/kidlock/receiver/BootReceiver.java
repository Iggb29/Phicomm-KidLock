package com.phicomm.kidlock.receiver;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import com.phicomm.kidlock.service.WatchdogService;

public class BootReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        Intent serviceIntent = new Intent(context, WatchdogService.class);
        context.startService(serviceIntent);
    }
}
