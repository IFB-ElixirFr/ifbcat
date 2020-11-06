from django.db import models


class Operation(models.Model):
    uri = models.TextField(blank=True, null=True)
    term = models.TextField(blank=True, null=True)
    # function = models.ForeignKey(Function, null=True, blank=True, related_name='operation', on_delete=models.CASCADE)

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode(self.term) or u''


# need to make this 0..many instead od 1..many
class Function(models.Model):
    # comment should be called note
    # I think cmd should be removed , doublecheck
    note = models.TextField(blank=True, null=True)
    cmd = models.CharField(max_length=500, blank=True, null=True)
    tool = models.ForeignKey(Tool, null=True, blank=True, related_name='function', on_delete=models.CASCADE)

    # many to many
    operation = models.ManyToManyField(Operation, blank=True)

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode(self.note) or u''


class Data(models.Model):
    uri = models.TextField(blank=True, null=True)
    term = models.TextField(blank=True, null=True)

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode(self.term) or u''


class Format(models.Model):
    uri = models.TextField(blank=True, null=True)
    term = models.TextField(blank=True, null=True)
    # input = models.ForeignKey(Input, null=True, blank=True, related_name='format', on_delete=models.CASCADE)
    # output = models.ForeignKey(Output, null=True, blank=True, related_name='format', on_delete=models.CASCADE)

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode(self.term) or u''


class Input(models.Model):
    # reverse relationship, because many inputs
    function = models.ForeignKey(Function, null=True, blank=True, related_name='input', on_delete=models.CASCADE)
    # forward relationship, because one data
    data = models.ForeignKey(Data, null=True, blank=False, related_name='input', on_delete=models.CASCADE)

    # many_to_many
    format = models.ManyToManyField(Format, blank=True)

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode(self.data.term) or u''


class Output(models.Model):
    # reverse relationship, because many outputs
    function = models.ForeignKey(Function, null=True, blank=True, related_name='output', on_delete=models.CASCADE)
    # forward relationship, because one data
    data = models.ForeignKey(Data, null=True, blank=False, related_name='output', on_delete=models.CASCADE)

    # many_to_many
    format = models.ManyToManyField(Format, blank=True)

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    # def __unicode__(self):
    #     return unicode(self.data.term) or u''
