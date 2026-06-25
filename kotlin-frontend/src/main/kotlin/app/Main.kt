package app

import androidx.compose.desktop.ui.tooling.preview.Preview
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.Button
import androidx.compose.material.MaterialTheme
import androidx.compose.material.Surface
import androidx.compose.material.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Fill
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Window
import androidx.compose.ui.window.application

import io.ktor.client.*
import io.ktor.client.engine.cio.*
import io.ktor.client.request.*
import io.ktor.client.statement.*
import io.ktor.client.call.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

@Serializable
data class CreateRequest(val name: String, val seed: Int? = null)

@Serializable
data class CreateResponse(val session_id: String, val state: LifeState)

@Serializable
data class ActionRequest(val session_id: String, val choice: String? = null)

@Serializable
data class ActionResponse(val state: LifeState, val event: String)

@Serializable
data class LifeState(
    val name: String,
    val age: Int,
    val alive: Boolean,
    val happiness: Int,
    val health: Int,
    val smarts: Int,
    val looks: Int,
    val money: Int,
    val married: Boolean,
    val children: Int,
    val career: String? = null,
    val history: List<List<kotlinx.serialization.json.JsonElement>>? = null
)

val client = HttpClient(CIO) {
    install(ContentNegotiation) {
        json(Json { ignoreUnknownKeys = true })
    }
}

@Composable
fun RetroScanlines(modifier: Modifier = Modifier) {
    Canvas(modifier = modifier) {
        val h = size.height
        val step = 4f
        var y = 0f
        while (y < h) {
            drawRect(Color(0f, 0f, 0f, 0.05f), topLeft = androidx.compose.ui.geometry.Offset(0f, y), size = androidx.compose.ui.geometry.Size(size.width, 1f), style = Fill)
            y += step
        }
    }
}

@Composable
fun MainUI() {
    var name by remember { mutableStateOf("") }
    var sessionId by remember { mutableStateOf<String?>(null) }
    var state by remember { mutableStateOf<LifeState?>(null) }
    var lastEvent by remember { mutableStateOf("") }
    var busy by remember { mutableStateOf(false) }

    Surface(modifier = Modifier.fillMaxSize(), color = Color(0xFF041A02)) {
        Box(modifier = Modifier.fillMaxSize()) {
            Column(modifier = Modifier.fillMaxSize().padding(24.dp)) {
                Text("Retro Life Simulator", fontSize = 28.sp, color = Color(0xFF7CFF6F), fontFamily = FontFamily.Monospace)
                Spacer(Modifier.height(12.dp))

                if (sessionId == null) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        androidx.compose.material.OutlinedTextField(value = name, onValueChange = { name = it }, label = { Text("Name") }, singleLine = true)
                        Spacer(Modifier.width(12.dp))
                        Button(onClick = {
                            busy = true
                            // create session
                            kotlinx.coroutines.GlobalScope.launch {
                                try {
                                    val resp = client.post("http://localhost:8000/create") {
                                        setBody(CreateRequest(name.ifBlank { "Player" }))
                                    }.body<CreateResponse>()
                                    sessionId = resp.session_id
                                    state = resp.state
                                } catch (e: Exception) {
                                    println("Create error: $e")
                                } finally {
                                    busy = false
                                }
                            }
                        }) { Text("Start") }
                    }
                } else {
                    state?.let { s ->
                        Text("Name: ${s.name}", color = Color(0xFF7CFF6F), fontFamily = FontFamily.Monospace)
                        Text("Age: ${s.age}  Money: ${s.money}", color = Color(0xFF7CFF6F), fontFamily = FontFamily.Monospace)
                        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            Column { Text("Health: ${s.health}", color = Color(0xFF7CFF6F)); Text("Happiness: ${s.happiness}", color = Color(0xFF7CFF6F)) }
                            Column { Text("Smarts: ${s.smarts}", color = Color(0xFF7CFF6F)); Text("Looks: ${s.looks}", color = Color(0xFF7CFF6F)) }
                        }
                        Spacer(Modifier.height(12.dp))
                        Text("Last event: $lastEvent", color = Color(0xFF9EFBA6), fontFamily = FontFamily.Monospace)
                        Spacer(Modifier.height(12.dp))
                        Row {
                            val choices = listOf("Work", "Study", "Exercise", "Party", "Risk")
                            for (c in choices) {
                                Button(onClick = {
                                    if (sessionId == null) return@Button
                                    busy = true
                                    kotlinx.coroutines.GlobalScope.launch {
                                        try {
                                            val resp = client.post("http://localhost:8000/action") {
                                                setBody(ActionRequest(sessionId!!, c))
                                            }.body<ActionResponse>()
                                            state = resp.state
                                            lastEvent = resp.event
                                        } catch (e: Exception) {
                                            println("Action error: $e")
                                        } finally {
                                            busy = false
                                        }
                                    }
                                }, modifier = Modifier.padding(end = 8.dp)) { Text(c, fontFamily = FontFamily.Monospace) }
                            }
                        }

                        Spacer(Modifier.height(12.dp))

                        Column(modifier = Modifier.fillMaxWidth().weight(1f)) {
                            Text("History:", color = Color(0xFF7CFF6F))
                            // show last 8 events from state.history if available
                            val hist = state.history
                            if (hist != null) {
                                val last = hist.takeLast(8)
                                for (h in last.reversed()) {
                                    // history items are lists like [age, "desc"] — show as text
                                    Text(h.toString(), color = Color(0xFF6EEB5E), fontFamily = FontFamily.Monospace)
                                }
                            }
                        }
                    }
                }
            }
            // scanlines overlay
            Box(Modifier.fillMaxSize()) {
                RetroScanlines(Modifier.fillMaxSize())
            }
        }
    }
}

@OptIn(ExperimentalStdlibApi::class)
@Composable
@Preview
fun AppPreview() {
    MainUI()
}

fun main() = application {
    Window(onCloseRequest = ::exitApplication, title = "Retro Life Simulator") {
        MaterialTheme {
            MainUI()
        }
    }
}
