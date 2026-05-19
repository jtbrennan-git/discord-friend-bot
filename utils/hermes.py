"""
Small subprocess wrapper for the optional Hermes CLI harness.
"""

import asyncio
import os
from dataclasses import dataclass
from typing import Optional, Sequence


@dataclass
class HermesResult:
    ok: bool
    output: str
    error: str = ""
    returncode: int = 0


class HermesClient:
    def __init__(
        self,
        binary: str = "hermes",
        profile: str = "discord-bot",
        provider: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: float = 60,
        max_output_chars: int = 4000,
    ):
        self.binary = binary
        self.profile = profile
        self.provider = provider
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.max_output_chars = max_output_chars

    def build_command(self, prompt: str, toolsets: str) -> Sequence[str]:
        cmd = [self.binary]
        if self.profile:
            cmd.extend(["-p", self.profile])
        cmd.append("chat")
        if self.provider:
            cmd.extend(["--provider", self.provider])
        if self.model:
            cmd.extend(["--model", self.model])
        if toolsets:
            cmd.extend(["--toolsets", toolsets])
        cmd.extend(["--quiet", "-q", prompt])
        return cmd

    async def ask(self, prompt: str, toolsets: str) -> HermesResult:
        env = os.environ.copy()
        if env.get("LLM_API_KEY") and not env.get("OPENROUTER_API_KEY"):
            env["OPENROUTER_API_KEY"] = env["LLM_API_KEY"]
        try:
            proc = await asyncio.create_subprocess_exec(
                *self.build_command(prompt, toolsets),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )
        except FileNotFoundError:
            return HermesResult(ok=False, output="", error=f"Hermes binary not found: {self.binary}", returncode=127)

        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=self.timeout_seconds)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.communicate()
            return HermesResult(ok=False, output="", error=f"Hermes timed out after {self.timeout_seconds:g}s", returncode=124)

        output = stdout.decode("utf-8", errors="replace").strip()
        error = stderr.decode("utf-8", errors="replace").strip()
        if len(output) > self.max_output_chars:
            output = output[: self.max_output_chars].rstrip() + "\n...[truncated]"
        if len(error) > self.max_output_chars:
            error = error[: self.max_output_chars].rstrip() + "\n...[truncated]"
        return HermesResult(ok=proc.returncode == 0, output=output, error=error, returncode=proc.returncode or 0)
