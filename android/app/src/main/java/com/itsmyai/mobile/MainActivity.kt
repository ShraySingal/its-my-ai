package com.itsmyai.mobile

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.itsmyai.mobile.network.ApiClient
import com.itsmyai.mobile.telemetry.DeviceTelemetryWorker

class MainActivity : ComponentActivity() {
    private val apiClient = ApiClient()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            CompanionScreen(
                onSyncClick = { serverUrl, callback ->
                    val battery = DeviceTelemetryWorker.getBatteryPercentage(this)
                    apiClient.sendHeartbeat(serverUrl, "phone_user_01", battery, "Android Smartphone") { success, msg ->
                        callback(success, battery, msg)
                    }
                }
            )
        }
    }
}

@Composable
fun CompanionScreen(onSyncClick: (String, (Boolean, Int, String?) -> Unit) -> Unit) {
    var serverUrl by remember { mutableStateOf("http://192.168.1.100:8000") }
    var statusText by remember { mutableStateOf("READY TO CONNECT") }
    var batteryLevel by remember { mutableStateOf(100) }
    var isConnected by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF030712))
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "IT'S MY AI MOBILE",
            color = Color(0xFF00F0FF),
            fontSize = 24.sp,
            fontFamily = FontFamily.Monospace
        )
        Text(
            text = "COMMAND CENTER COMPANION",
            color = Color(0xFF94A3B8),
            fontSize = 12.sp,
            fontFamily = FontFamily.Monospace,
            modifier = Modifier.padding(bottom = 24.dp)
        )

        OutlinedTextField(
            value = serverUrl,
            onValueChange = { serverUrl = it },
            label = { Text("Command Center Server URL", color = Color(0xFF38BDF8)) },
            placeholder = { Text("http://192.168.x.x:8000") },
            singleLine = true,
            colors = OutlinedTextFieldDefaults.colors(
                focusedTextColor = Color(0xFFE2E8F0),
                unfocusedTextColor = Color(0xFFE2E8F0),
                focusedBorderColor = Color(0xFF00F0FF),
                unfocusedBorderColor = Color(0xFF475569)
            ),
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(16.dp))

        Card(
            colors = CardDefaults.cardColors(containerColor = Color(0xFF0F172A)),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(20.dp)) {
                Text(
                    text = "DEVICE TELEMETRY",
                    color = Color(0xFF38BDF8),
                    fontSize = 14.sp,
                    fontFamily = FontFamily.Monospace
                )
                Spacer(modifier = Modifier.height(12.dp))
                Text(text = "Status: $statusText", color = if (isConnected) Color(0xFF10B981) else Color(0xFFE2E8F0))
                Text(text = "Battery Sync: $batteryLevel%", color = Color(0xFFE2E8F0))
                Text(text = "Device ID: phone_user_01", color = Color(0xFF94A3B8), fontSize = 12.sp)
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        Button(
            onClick = {
                statusText = "CONNECTING..."
                onSyncClick(serverUrl) { success, battery, _ ->
                    isConnected = success
                    batteryLevel = battery
                    statusText = if (success) "ONLINE — PAIRED WITH LAPTOP" else "OFFLINE (CHECK SERVER IP)"
                }
            },
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF00F0FF))
        ) {
            Text(text = "SYNC WITH LAPTOP COMMAND CENTER", color = Color(0xFF030712))
        }
    }
}
