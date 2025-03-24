from django.db import models
import uuid
import logging

logger = logging.getLogger('job_posting')

class JobPostingManager(models.Manager):
    async def acreate(self, **kwargs):
        instance = self.model(**kwargs)
        await instance.asave()
        return instance

class JobPosting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, db_index=True)
    company = models.CharField(max_length=200, db_index=True)
    required_skills = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = JobPostingManager()

    class Meta:
        indexes = [
            models.Index(fields=['title', 'company']),
        ]
        ordering = ['-created_at']

    async def asave(self, *args, **kwargs):
        await super().asave(*args, **kwargs)
        logger.info(f"Job posting saved: {self.id} - {self.title}")

    def __str__(self):
        return f"{self.title} - {self.company}"