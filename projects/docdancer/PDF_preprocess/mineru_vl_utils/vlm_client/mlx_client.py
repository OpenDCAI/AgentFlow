# Copyright (c) Opendatalab. All rights reserved.
import asyncio
from typing import Sequence
from PIL import Image
from tqdm import tqdm

from .base_client import (VlmClient,
                          SamplingParams,
                          DEFAULT_USER_PROMPT,
                          DEFAULT_SYSTEM_PROMPT)


class MlxVlmClient(VlmClient):

    def __init__(
            self,
            model,  # MLX model object
            processor,  # MLX processor object
            prompt: str = DEFAULT_USER_PROMPT,
            system_prompt: str = DEFAULT_SYSTEM_PROMPT,
            sampling_params: SamplingParams | None = None,
            text_before_image: bool = False,
            allow_truncated_content: bool = False,
            batch_size: int = 1,
            use_tqdm: bool = True,
    ):
        super().__init__(
            prompt=prompt,
            system_prompt=system_prompt,
            sampling_params=sampling_params,
            text_before_image=text_before_image,
            allow_truncated_content=allow_truncated_content,
        )
        self.model = model
        self.processor = processor
        self.batch_size = batch_size
        self.use_tqdm = use_tqdm
        self.model_max_length = model.config.text_config.max_position_embeddings
        try:
            from mlx_vlm import generate
            self.generate = generate
        except ImportError:
            raise ImportError("Please install mlx-vlm to use the mlx-engine backend.")

    def build_messages(self, prompt: str) -> list[dict]:
        prompt = prompt or self.prompt
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        if "<image>" in prompt:
            prompt_1, prompt_2 = prompt.split("<image>", 1)
            user_messages = [
                *([{"type": "text", "text": prompt_1}] if prompt_1.strip() else []),
                {"type": "image"},
                *([{"type": "text", "text": prompt_2}] if prompt_2.strip() else []),
            ]
        elif self.text_before_image:
            user_messages = [
                {"type": "text", "text": prompt},
                {"type": "image"},
            ]
        else:  # image before text, which is the default behavior.
            user_messages = [
                {"type": "image"},
                {"type": "text", "text": prompt},
            ]
        messages.append({"role": "user", "content": user_messages})
        return messages

    def build_generate_kwargs(self, sampling_params: SamplingParams | None):
        sp = self.build_sampling_params(sampling_params)
        generate_kwargs = {
            "temperature": sp.temperature,
            "top_p": sp.top_p,
            "top_k": sp.top_k,
            "presence_penalty": sp.presence_penalty,
            "frequency_penalty": sp.frequency_penalty,
            "repetition_penalty": sp.repetition_penalty,
            # max_tokens should smaller than model max length
            "max_tokens": sp.max_new_tokens if sp.max_new_tokens is not None else self.model_max_length,
        }
        return generate_kwargs

    def predict(
            self,
            image: Image.Image | bytes | str,
            prompt: str = "",
            sampling_params: SamplingParams | None = None,
            priority: int | None = None,
    ) -> str:

        chat_prompt = self.processor.apply_chat_template(
            self.build_messages(prompt),
            tokenize=False,
            add_generation_prompt=True,
        )

        generate_kwargs = self.build_generate_kwargs(sampling_params)

        response = self.generate(
            model=self.model,
            processor=self.processor,
            prompt=chat_prompt,
            image=image,
            **generate_kwargs,
        )
        return response.text

    def batch_predict(
            self,
            images: Sequence[Image.Image | bytes | str],
            prompts: Sequence[str] | str = "",
            sampling_params: Sequence[SamplingParams | None] | SamplingParams | None = None,
            priority: Sequence[int | None] | int | None = None,
    ) -> list[str]:
        results = []

        images_len = len(images)

        if isinstance(prompts, str):
            prompts = [prompts] * images_len
        if not isinstance(sampling_params, Sequence):
            sampling_params = [sampling_params] * images_len

        with tqdm(total=images_len, desc="Predict", disable=not self.use_tqdm) as pbar:

            # Since mlx-vlm's generate function does not support batching, we can only call it in a loop
            for i in range(0, images_len):
                result = self.predict(
                    image=images[i],
                    prompt=prompts[i],
                    sampling_params=sampling_params[i],
                )
                results.append(result)
                pbar.update(1)

        return results

    async def aio_predict(
            self,
            image: Image.Image | bytes | str,
            prompt: str = "",
            sampling_params: SamplingParams | None = None,
            priority: int | None = None,
    ) -> str:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            self.predict,
            image,
            prompt,
            sampling_params,
            priority,
        )

    async def aio_batch_predict(
            self,
            images: Sequence[Image.Image | bytes | str],
            prompts: Sequence[str] | str = "",
            sampling_params: Sequence[SamplingParams | None] | SamplingParams | None = None,
            priority: Sequence[int | None] | int | None = None,
            semaphore: asyncio.Semaphore | None = None,
            use_tqdm=False,
            tqdm_desc: str | None = None,
    ) -> list[str]:
        return await asyncio.to_thread(
            self.batch_predict,
            images,
            prompts,
            sampling_params,
            priority,
        )
